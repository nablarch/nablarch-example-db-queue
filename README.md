# nablarch-example-db-queue

Nablarch Application Frameworkのデータベースのテーブルをキューとして扱うメッセージング処理のExampleです。

このExampleでは、 ``INS_PROJECT_RECEIVE_MESSAGE`` テーブルをキューとして扱い、定期的に監視します。
キュー内に未処理のデータが存在した場合、そのデータを ``PROJECT`` テーブルへと移送します。

## 実行手順

### 1.動作環境
実行環境に以下のソフトウェアがインストールされている事を前提とします。
* Java Version : 8
* Maven 3.0.5以降

なお、このアプリケーションはH2 Database Engineを組み込んでいます。別途DBサーバのインストールは必要ありません。

### 2. プロジェクトリポジトリの取得
Gitを使用している場合、アプリケーションを配置したいディレクトリにて「git clone」コマンドを実行してください。
以下、コマンドの例です。

    $mkdir c:\example
    $cd c:\example
    $git clone https://github.com/nablarch/nablarch-example-db-queue.git

Gitを使用しない場合、最新のタグからzipをダウンロードし、任意のディレクトリへ展開してください。

### 3. アプリケーションのビルド
次に、アプリケーションをビルドします。以下のコマンドを実行してください。

    $cd nablarch-example-db-queue
    $mvn clean package

### 4. アプリケーションの起動
以下のコマンドでアプリケーションを起動します。

```
    mvn exec:java -Dexec.mainClass=nablarch.fw.launcher.Main -Dexec.args="'-diConfig' 'com/nablarch/example/app/batch/project-creation-service.xml' '-requestPath' 'ProjectCreationService' '-userId' 'samp'"
```

なお、 `maven-assembly-plugin` を使用して実行可能jarの生成を行っているため、以下のコマンドでもアプリケーションを実行することが可能です。

1. ``target/application-<version_no>.zip`` を任意のディレクトリに解凍する。
2. 以下のコマンドにて実行する

  ```
      java -jar <1で解凍したディレクトリ名>/nablarch-example-db-queue-<version_no>.jar -diConfig com/nablarch/example/app/batch/project-creation-service.xml -requestPath ProjectCreationService -userId sample
  ```

### 5. DBの確認方法

1. http://www.h2database.com/html/cheatSheet.html からH2をインストールしてください。

2. {インストールフォルダ}/bin/h2.bat を実行してください(コマンドプロンプトが開く)。
  ※h2.bat実行中はExampleアプリケーションからDBへアクセスすることができないため、Exampleアプリケーションを停止しておいてください。

3. ブラウザから http://localhost:8082 を開き、以下の情報でH2コンソールにログインしてください。
   JDBC URLの{dbファイルのパス}には、`nablarch_example_db_queue.mv.db`ファイルの格納ディレクトリまでのパスを指定してください。  
  JDBC URL：jdbc:h2:{dbファイルのパス}/nablarch_example_db_queue  
  ユーザ名：SAMPLE  
  パスワード：SAMPLE  

### 6. 動作確認
監視対象テーブルの``INS_PROJECT_RECEIVE_MESSAGE``にデータを投入することで、
プロジェクトテーブルにデータが作成されます。
(本ExampleアプリケーションではDBにH2を使用しているため、
アプリケーション起動中に別のプロセスからDBを操作することができません。
そのため、アプリケーションを停止し、「5. DBの確認方法」を参考にH2コンソールからデータを投入してください。)

投入SQLの例
```sql
    insert into ins_project_receive_message (
        received_message_sequence,
        project_name,
        project_type,
        project_class,
        project_start_date,
        project_end_date,
        client_id,
        project_manager,
        project_leader,
        user_id,
        note,
        sales,
        cost_of_goods_sold,
        sga,
        allocation_of_corp_expenses,
        status
    ) values (
        2,
        'プロジェクト名',
        'development',
        '分類',
        '2011-01-01',
        '2020-12-31',
        1,
        'admin',
        'user1',
        1,
        ' ',
        100,
        200,
        300,
        400,
        '0'
     )
```

アプリケーションは自動で終了しないので、プロセスを強制終了(Ctrl + C)してください。
※プロダクション環境では、プロセス停止ハンドラを使うことで安全にプロセスを終了できます。
