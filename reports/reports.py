from geraldo import ObjectValue, DetailBand, Label, Report, ReportBand, SystemField
from geraldo.utils import cm, BAND_WIDTH, TA_CENTER, TA_RIGHT

class RequestReport(Report):
    title = 'HTTP request report'

    class band_detail(DetailBand):
        height = 0.7*cm
        elements = [
            ObjectValue(expression='type', left=0.5*cm, style={'fontSize': 9}),
            ObjectValue(expression='name', left=2.3*cm, style={'fontSize': 9}),
            ObjectValue(expression='value', left=7*cm, style={'fontSize': 9}),
        ]


