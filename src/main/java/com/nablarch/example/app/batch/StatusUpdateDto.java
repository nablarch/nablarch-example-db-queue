package com.nablarch.example.app.batch;

/**
 * ステータスを更新するための情報を持つBean。
 *
 * @author Nabu Rakutaro
 */
public final class StatusUpdateDto {

    /** id */
    private final String id;

    /** 更新後のステータス */
    private final String newStatus;

    /**
     * Beanを生成する。
     * @param id ID
     * @param newStatus 更新後のステータス
     */
    public StatusUpdateDto(final String id, final String newStatus) {
        this.id = id;
        this.newStatus = newStatus;
    }

    /**
     * IDを取得する。
     * @return ID
     */
    public String getId() {
        return id;
    }

    /**
     * 更新後のステータスを取得する。
     * @return 更新後のステータス
     */
    public String getNewStatus() {
        return newStatus;
    }

    /**
     * 正常終了を示すオブジェクトを生成する。
     *
     * @param targetId ステータス更新対象のID
     * @return 生成したオブジェクト
     */
    public static StatusUpdateDto createNormalEnd(final String targetId) {
        return new StatusUpdateDto(targetId, "1");
    }

    /**
     * 異常終了を示すオブジェクトを生成する。
     *
     * @param targetId ステータス更新対象のID
     * @return 生成したオブジェクト
     */
    public static StatusUpdateDto createAbnormalEnd(final String targetId) {
        return new StatusUpdateDto(targetId, "2");
    }
}

