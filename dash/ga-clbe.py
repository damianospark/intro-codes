#!/usr/bin/env python

from google.analytics.data_v1beta.types import (
    DateRange,
    Dimension,
    Metric,
    RunReportRequest,
)
from google.analytics.data_v1beta import BetaAnalyticsDataClient
import os
from datetime import datetime, timedelta

# Set the value of an environment variable
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = './cleanbedding-c9b48eb044cf-service-account-key.json'

# Retrieve the value of the environment variable
# my_var_value = os.environ.get('MY_VAR')

# print(my_var_value)  # Output: my_value
"""Google Analytics Data API sample quickstart application.
This application demonstrates the usage of the Analytics Data API using
service account credentials.
Before you start the application, please review the comments starting with
"TODO(developer)" and update the code to use correct values.
Usage:
  pip3 install --upgrade google-analytics-data
  python3 quickstart.py
"""
# [START analyticsdata_quickstart]


def to_csv(report_response):
    import csv
    from google.analytics.data_v1beta.types import analytics_data_api

    original_list = [
        dimension.name for dimension in report_response.dimension_headers]
    new_list = [metric.name for metric in report_response.metric_headers]
    index = -3
    # Get the header names from the report metadata
    header = original_list[:index + 1] + new_list + original_list[index + 1:]

    # Get the data rows from the report data
    rows = []
    for row in report_response.rows:
        original_list = [dimension.value for dimension in row.dimension_values]
        new_list = [metric.value for metric in row.metric_values]
        index = -3
        row_values = original_list[:index + 1] + \
            new_list + original_list[index + 1:]
        rows.append(row_values)

    # Write the CSV file
    with open('report.csv', 'w', newline='') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(header)
        writer.writerows(rows)


# '289131905'  #PROPERTY ID in "admin > Property Settings > right fpanel in the right corner GA4
def sample_run_report(property_id="289131905"):
    """Runs a simple report on a Google Analytics 4 property."""
    # cleanb.life pid : 387495261
    # [START analyticsdata_run_report_initialize]
    # Using a default constructor instructs the client to use the credentials
    # specified in GOOGLE_APPLICATION_CREDENTIALS environment variable.
    client = BetaAnalyticsDataClient()
    # [END analyticsdata_run_report_initialize]

    # Get today's date
    today = datetime.now()
    # Calculate the date 6 months ago
    six_months_ago = today - timedelta(days=6 * 30)
    # Format the date as YYYY-mm-dd
    date_from = six_months_ago.strftime('%Y-%m-%d')

    # [START analyticsdata_run_report]
    request = RunReportRequest(
        property=f"properties/{property_id}",
        dimensions=[
            Dimension(name="date"),
            Dimension(name="firstSessionDate"),
            Dimension(name="firstUserSourceMedium"),
            Dimension(name="firstUserManualTerm"),
            Dimension(name="firstUserManualAdContent"),
            # Dimension(name="firstUserGoogleAdsCampaignName"), #!이게 포함되면 구글로 유입된 데이터만 추출됨
            Dimension(name="campaignName"),
            Dimension(name="pageReferrer"),
            # -deviceCategory, platform, userAgeBracket,userGender, brandingInterest, audienceName, city
            Dimension(name="landingPagePlusQueryString"),
        ],
        metrics=[
            # Metric(name="newUsers"),
            Metric(name="conversions"),
            # Metric(name="totalUsers"),
            # Metric(name="transactions"),
            # Metric(name="checkouts"),
            # Metric(name="totalPurchasers"),
            # Metric(name="engagedSessions"),
            # Metric(name="userEngagementDuration"),
            # Metric(name="bounceRate"),
        ],
        # date_ranges=[DateRange(start_date="2023-01-01", end_date="today")],
        date_ranges=[DateRange(start_date=date_from, end_date="today")],
    )
    # *engagement      : sessions that lasted longer than 10 seconds, or had a conversion event, or had 2 or more screen views.
    # *Engagement rate : The percentage of engaged sessions (Engaged sessions divided by Sessions). This metric is returned as a fraction; for example, 0.7239 means 72.39% of sessions were engaged sessions.
    # *Bounce rate     : The percentage of sessions that were not engaged ((Sessions Minus Engaged sessions) divided by Sessions). This metric is returned as a fraction; for example, 0.2761 means 27.61% of sessions were bounces.
    # *Conversions     : The count of conversion events. Events are marked as conversions at collection time; changes to an event's conversion marking apply going forward. You can mark any event as a conversion in Google Analytics, and some events (i.e. first_open, purchase) are marked as conversions by default. To learn more, see https://support.google.com/analytics/answer/9267568.
    # TODO more details --> https://developers.google.com/analytics/devguides/reporting/data/v1/api-schema

    response = client.run_report(request)
    to_csv(response)
    # [END analyticsdata_run_report]

    # [START analyticsdata_run_report_response]
    # print("Report result:", response.dimension_headers, response.metric_headers)
    #!google.analytics.data_v1beta.types.analytics_data_api.RunReportResponse
    # ? dimension_headers : [name: "date", name: "pagePath", name: "firstUserSourceMedium", name: firstUserManualTerm", name: "firstUserManualAdContent",name: "pageReferrer"]
    # ? metric_headers : [name: "firstUsers" type_: TYPE_INTEGER]
    # for row in response.rows:
    #     print(row.dimension_values)
    # print(row.dimension_values[0].value, row.metric_values[0].value)
    # [END analyticsdata_run_report_response]


# [END analyticsdata_quickstart]

if __name__ == "__main__":
    sample_run_report()
