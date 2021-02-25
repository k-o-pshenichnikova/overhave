from datetime import datetime, timedelta
from typing import Optional, Sequence

import pytest
from markupsafe import Markup
from pytest_mock import MockerFixture

from overhave import db
from overhave.admin.views import FeatureView, TestRunView, datetime_formatter, result_report_formatter, task_formatter
from overhave.admin.views.formatters import feature_name_formatter
from overhave.db import TestReportStatus, TestRun, TestRunStatus
from overhave.utils import get_current_time


class TestDatetimeFormatter:
    """ Unit tests for datetime_formatter. """

    def test_empty_status(self, test_testrun_view: TestRunView, mocker: MockerFixture):
        assert datetime_formatter(
            view=test_testrun_view, context=mocker.MagicMock(), model=TestRun(), name="start"
        ) == Markup("")

    @pytest.mark.parametrize(
        ("column_name", "time"),
        [
            ("created_at", get_current_time()),
            ("start", get_current_time() + timedelta(seconds=1)),
            ("end", get_current_time() + timedelta(seconds=5)),
        ],
    )
    def test_time(
        self, test_testrun_view, mocker: MockerFixture, test_testrun_id: int, column_name: str, time: datetime
    ):
        result = datetime_formatter(
            view=test_testrun_view,
            context=mocker.MagicMock(),
            model=TestRun(**{"id": test_testrun_id, column_name: time}),
            name=column_name,
        )
        assert result == Markup(time.strftime("%d-%m-%Y %H:%M:%S"))


class TestResultReportFormatter:
    """ Unit tests for result_report_formatter. """

    def test_empty_status(self, test_testrun_view: TestRunView, mocker: MockerFixture):
        assert result_report_formatter(
            view=test_testrun_view, context=mocker.MagicMock(), model=TestRun(), name="status"
        ) == Markup("")

    @pytest.mark.parametrize("status", list(TestRunStatus))
    @pytest.mark.parametrize("report_status", [x for x in list(TestReportStatus) if not x.has_report])
    def test_no_report(
        self,
        test_testrun_view,
        mocker: MockerFixture,
        test_testrun_id: int,
        status: TestRunStatus,
        report_status: TestReportStatus,
        test_testrun_button_css_class: str,
    ):
        result = result_report_formatter(
            view=test_testrun_view,
            context=mocker.MagicMock(),
            model=TestRun(id=test_testrun_id, status=status, report_status=report_status),
            name="status",
        )
        assert result == Markup(
            f"<a href='/testrun/details/?id={test_testrun_id}'"
            f"<form action='#'>"
            f"<fieldset title='Show details'>"
            f"<button class='link-button {test_testrun_button_css_class}'>{status}</button>"
            "</fieldset>"
            "</form>"
            "</a>"
        )

    @pytest.mark.parametrize("status", list(TestRunStatus))
    @pytest.mark.parametrize("report_status", [x for x in list(TestReportStatus) if x.has_report])
    def test_with_report(
        self,
        test_testrun_view,
        mocker: MockerFixture,
        test_testrun_id: int,
        status: TestRunStatus,
        report_status: TestReportStatus,
        test_testrun_report_link: Optional[str],
        test_testrun_button_css_class: str,
    ):
        result = result_report_formatter(
            view=test_testrun_view,
            context=mocker.MagicMock(),
            model=TestRun(
                id=test_testrun_id, status=status, report_status=report_status, report=test_testrun_report_link
            ),
            name="status",
        )
        assert result == Markup(
            f"<a href='/reports/{test_testrun_report_link}' target='_blank'"
            f"<form action='#'>"
            f"<fieldset title='Go to report'>"
            f"<button class='link-button {test_testrun_button_css_class}'>{status}</button>"
            "</fieldset>"
            "</form>"
            "</a>"
        )


@pytest.mark.parametrize("tasks", [("TCS-123",), ("TCS-456", "TCS-789")])
class TestTaskFormatter:
    """ Unit tests for task_formatter. """

    @pytest.mark.parametrize("test_browse_url", [None], indirect=True)
    def test_task_without_url(
        self, test_browse_url: None, test_feature_view: FeatureView, tasks: Sequence[str], mocker: MockerFixture,
    ):
        assert task_formatter(
            view=test_feature_view, context=mocker.MagicMock(), model=db.Feature(task=tasks), name="task",
        ) == Markup(", ".join(tasks))

    @pytest.mark.parametrize("test_browse_url", ["https://overhave.readthedocs.io"], indirect=True)
    def test_task_with_url(
        self, test_browse_url: str, test_feature_view: FeatureView, tasks: Sequence[str], mocker: MockerFixture,
    ):
        task_links = []
        for task in tasks:
            task_links.append(f"<a href='{test_browse_url}/{task}' target='blank'>{task}</a>")
        assert task_formatter(
            view=test_feature_view, context=mocker.MagicMock(), model=db.Feature(task=tasks), name="task",
        ) == Markup(", ".join(task_links))


@pytest.mark.parametrize("test_browse_url", [None], indirect=True)
class TestFeatureNameFormatter:
    """ Unit tests for feature_name_formatter. """

    def test_empty_name(self, test_feature_view: TestRunView, mocker: MockerFixture):
        assert feature_name_formatter(
            view=test_feature_view, context=mocker.MagicMock(), model=db.Feature(), name="name"
        ) == Markup("")

    def test_with_name(
        self, test_feature_view: TestRunView, mocker: MockerFixture, test_feature_id: int, test_feature_name: str
    ):
        assert feature_name_formatter(
            view=test_feature_view,
            context=mocker.MagicMock(),
            model=db.Feature(id=test_feature_id, name=test_feature_name),
            name="name",
        ) == Markup(f"<a href='/feature/edit/?id={test_feature_id}'>{test_feature_name}</a>")
