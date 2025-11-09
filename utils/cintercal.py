from datetime import datetime, timedelta
import math
def trunc(num, digits):
    factor = 10 ** digits
    return math.trunc(num * factor) / factor

def calculate_interest_components(df, sofr_df, opstype,prdtype, ratetype, fundertype,
                                  xdj_switch):
    fixed_funder_intrate = 10
    principal_amount = df.loc[(df["field"] == "Repayment") & (df["section"] == "Funder Transaction"), "value"].iloc[0]
    outstanding_principal = df.loc[(df["field"] == "Outstanding Principal") & (df["section"] == "SME Transaction"), "value"].iloc[0]
    drawdown_date = df.loc[(df["field"] == "SME Disbursement Date") & (df["section"] == "Payment Details"), "value"].iloc[0]
    lastfundersub_date = df.loc[(df["field"] == "Last Funder Submission Date") & (df["section"] == "Funder Information"), "value"].iloc[0]
    tenor_days = df.loc[(df["field"] == "Tenor (Days)") & (df["section"] == "SME Information"), "value"].iloc[0]
    expected_repaydate = drawdown_date + timedelta(days=tenor_days)
    if prdtype == "RFPO":
        drawdown_date = lastfundersub_date if lastfundersub_date is not None else drawdown_date
        principal_amount = outstanding_principal
    else:
        t0_method = drawdown_date >= datetime(2025, 6, 23)
        drawdown_date -= timedelta(days=1 if t0_method else 0)

    mit_hdays = df.loc[(df["field"] == "MIT (Days)") & (df["section"] == "SME Information"), "value"].iloc[0]
    mitrepaydue_date = drawdown_date + timedelta(mit_hdays)
    repayment_date = df.loc[(df["field"] == "Repayment Date") & (df["section"] == "Payment Details"), "value"].iloc[0]
    if opstype == "Rollover":
        repayment_date -= timedelta(days=1)
    
    sme_rate = df.loc[(df["field"] == "Interest Rate (% p.a.)") & (df["section"] == "Funder Information"), "value"].iloc[0]
    platform_fee = df.loc[(df["field"] == "Platform Fee") & (df["section"] == "Funder Transaction"), "value"].iloc[0]
    waived_interest = df.loc[(df["field"] == "Interest") & (df["section"] == "Waive Items"), "value"].iloc[0] + \
                      df.loc[(df["field"] == "Overdue Interest") & (df["section"] == "Waive Items"), "value"].iloc[0]
    waived_bankcharge = df.loc[(df["field"] == "Bank Charge") & (df["section"] == "Waive Items"), "value"].iloc[0]
    surcharge_item = df.loc[(df["field"] == "Others") & (df["section"] == "Surcharge Items"), "value"].iloc[0]

    float_rate = 'Daily Calculated Blended HIBOR' if ratetype == 'HIBOR+' else 'SOFR'
    hdays = (repayment_date - drawdown_date).days
    regul_floatsum = sofr_df.loc[(sofr_df['Calculation Date'] > drawdown_date) & 
                                 (sofr_df['Calculation Date'] <= repayment_date), float_rate].sum()

    overdue_interest = 0
    if repayment_date <= mitrepaydue_date:
        note = "MIT"
        mit_fillrate = sofr_df.loc[(sofr_df['Calculation Date'] == repayment_date), float_rate].iloc[0]
        floatsum = (mit_hdays - hdays) * mit_fillrate + regul_floatsum
        hdays = mit_hdays
    elif repayment_date > expected_repaydate:
        note = "Overdue"
        overdue_hdays = (repayment_date - expected_repaydate).days
        overduesum = sofr_df.loc[(sofr_df['Calculation Date'] > drawdown_date) & 
                                 (sofr_df['Calculation Date'] <= repayment_date), float_rate].sum()
    else:
        note = "Normal"
        floatsum = regul_floatsum

    sme_interest = 0
    overdue_interest = 0
    if ratetype in ["SOFR+", "HIBOR+"]:
        sme_interest = trunc((floatsum + sme_rate * hdays) / 360 * principal_amount * 0.01, 2)
        if note == "Overdue":
            overdue_interest = trunc((overduesum + sme_rate * overdue_hdays) / 360 * principal_amount * 0.01, 2)
        if note != "Overdue" or prdtype in ["PL-novd", "RFPO"]:
            overdue_interest = 0
    elif ratetype == "Fixed":
        if fundertype == "Fixed":
            sme_rate = fixed_funder_intrate
        sme_interest = trunc((sme_rate * hdays) / 360 * principal_amount * 0.01, 2)
        if note == "Overdue":
            overdue_interest = trunc((sme_rate * overdue_hdays) / 360 * principal_amount * 0.01, 2)
        if note != "Overdue" or prdtype in ["PL-novd", "RFPO"]:
            overdue_interest = 0

    funder_interest = sme_interest + overdue_interest
    if xdj_switch == 0:
        funder_interest += surcharge_item - waived_interest
        if funder_interest >= waived_bankcharge and fundertype == "Main":
            funder_interest -= waived_bankcharge

    if platform_fee != 0:
        platform_fee = funder_interest * 0.01 * -1
    else:
        platform_fee = 0

    if xdj_switch:
        funder_interest += surcharge_item
        if funder_interest >= waived_bankcharge and fundertype == "Main":
            funder_interest -= waived_bankcharge

    if fundertype == "Zero":
        funder_interest = 0

    spreading = (sme_interest + overdue_interest) + surcharge_item - waived_bankcharge - waived_interest - funder_interest

    return sme_interest, overdue_interest, funder_interest, spreading,note