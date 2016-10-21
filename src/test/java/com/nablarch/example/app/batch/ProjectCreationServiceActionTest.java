package com.nablarch.example.app.batch;

import nablarch.test.core.batch.BatchRequestTestSupport;

import org.junit.Test;

/**
 * {@link ProjectCreationServiceAction}のテストクラス。
 */
public class ProjectCreationServiceActionTest extends BatchRequestTestSupport {

    @Test
    public void 正常にプロジェクト情報が取り込まれるケース() throws Exception {
        execute();
    }

    @Test
    public void プロジェクトの取り込みに失敗するケース() throws Exception {
        execute();
    }
}