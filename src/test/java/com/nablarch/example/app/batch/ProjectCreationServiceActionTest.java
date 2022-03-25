package com.nablarch.example.app.batch;

import nablarch.test.core.batch.BatchRequestTestSupport;

import nablarch.test.junit5.extension.batch.BatchRequestTest;
import org.junit.jupiter.api.Test;

/**
 * {@link ProjectCreationServiceAction}のテストクラス。
 */
@BatchRequestTest
class ProjectCreationServiceActionTest {

    BatchRequestTestSupport support;

    @Test
    void 正常にプロジェクト情報が取り込まれるケース() throws Exception {
        support.execute(support.testName.getMethodName());
    }

    @Test
    void プロジェクトの取り込みに失敗するケース() throws Exception {
        support.execute(support.testName.getMethodName());
    }
}