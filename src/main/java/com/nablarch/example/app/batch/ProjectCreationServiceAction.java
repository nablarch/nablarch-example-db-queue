package com.nablarch.example.app.batch;

import java.util.Collections;
import java.util.Date;
import java.util.HashMap;
import java.util.Map;
import java.util.UUID;
import java.util.function.Function;

import com.nablarch.example.app.entity.Project;

import nablarch.common.dao.UniversalDao;
import nablarch.core.db.connection.AppDbConnection;
import nablarch.core.db.statement.SqlRow;
import nablarch.core.db.transaction.SimpleDbTransactionExecutor;
import nablarch.core.db.transaction.SimpleDbTransactionManager;
import nablarch.core.message.ApplicationException;
import nablarch.core.message.MessageLevel;
import nablarch.core.message.MessageUtil;
import nablarch.core.repository.SystemRepository;
import nablarch.fw.DataReader;
import nablarch.fw.ExecutionContext;
import nablarch.fw.Result;
import nablarch.fw.Result.Success;
import nablarch.fw.action.BatchAction;
import nablarch.fw.reader.DatabaseRecordReader;
import nablarch.fw.reader.DatabaseTableQueueReader;

/**
 * 受信テーブルを入力としてプロジェクト情報を作成する常駐サービス。
 *
 * @author Nabu Rakutaro
 */
public class ProjectCreationServiceAction extends BatchAction<SqlRow> {

    /** SQLIDのプレフィックス */
    private static final String SQL_ID_PREFIX = ProjectCreationServiceAction.class.getName() + '#';

    /** プロセスIDを保持するマップ */
    private static final Map<String, String> PROCESS_MAP;

    static {
        Map<String, String> map = new HashMap<>();
        map.put("processId", UUID.randomUUID().toString());
        PROCESS_MAP = Collections.unmodifiableMap(map);
    }

    @Override
    public Result handle(final SqlRow inputData, final ExecutionContext ctx) {

        final Project project = UniversalDao.findBySqlFile(
                Project.class,
                SQL_ID_PREFIX + "GET_RECEIVED_PROJECT",
                inputData);

        if (!isValidProjectPeriod(project)) {
            throw new ApplicationException(MessageUtil.createMessage(MessageLevel.ERROR, "abnormal.project.period"));
        }

        UniversalDao.insert(project);

        return new Success();
    }

    /**
     * プロジェクトの期間が有効かどうか。
     * <p>
     * 開始が終了より後の場合は無効と判断する。
     *
     * @param project プロジェクト
     * @return プロジェクトの期間が有効または未指定の場合は{@code true}
     */
    private static boolean isValidProjectPeriod(final Project project) {
        if (project == null) {
            return true;
        }
        final Date startDate = project.getProjectStartDate();
        final Date endDate = project.getProjectEndDate();
        return startDate == null || endDate == null || startDate.compareTo(endDate) <= 0;
    }

    /**
     * 正常終了時には、ステータスを処理済みに更新する。
     */
    @Override
    protected void transactionSuccess(final SqlRow inputData, final ExecutionContext context) {
        updateStatus(inputData, StatusUpdateDto::createNormalEnd);
    }

    /**
     * 異常終了時には、ステータスを異常に更新する。
     */
    @Override
    protected void transactionFailure(final SqlRow inputData, final ExecutionContext context) {
        updateStatus(inputData, StatusUpdateDto::createAbnormalEnd);
    }

    /**
     * ステータスの更新処理を実行する。
     *
     * @param inputData 入力データ
     * @param function ステータス更新DTOのインスタンスを生成する関数
     */
    private void updateStatus(final SqlRow inputData, final Function<String, StatusUpdateDto> function) {
        getParameterizedSqlStatement("UPDATE_STATUS")
                .executeUpdateByObject(function.apply(inputData.getString("RECEIVED_MESSAGE_SEQUENCE")));
    }

    @Override
    public DataReader<SqlRow> createReader(final ExecutionContext ctx) {
        final DatabaseRecordReader databaseRecordReader = new DatabaseRecordReader();
        databaseRecordReader.setStatement(getParameterizedSqlStatement("FIND_RECEIVED_PROJECTS"), PROCESS_MAP);
        databaseRecordReader.setListener(() -> {
            final SimpleDbTransactionManager transactionManager = SystemRepository.get("redundancyTransaction");
            new SimpleDbTransactionExecutor<Void>(transactionManager) {
                @Override
                public Void execute(final AppDbConnection appDbConnection) {
                    appDbConnection
                            .prepareParameterizedSqlStatementBySqlId(SQL_ID_PREFIX + "UPDATE_PROCESS_ID")
                            .executeUpdateByMap(PROCESS_MAP);
                    return null;
                }
            }.doTransaction();

        });
        return new DatabaseTableQueueReader(databaseRecordReader, 1000, "RECEIVED_MESSAGE_SEQUENCE");
    }

}

