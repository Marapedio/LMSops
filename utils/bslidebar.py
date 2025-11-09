#———————Funder ID settings: Funder
def get_funder_type(df):
    funder_id = str(df.loc[(df["field"] == "Funder ID") & (df["section"] == "Funder Information"), "value"].iloc[0])
    zero_intrate_funder = ['FP0045', 'FP0049' , 'FP0056','FP0055','FP0000']
    notzero_intrate_funder = ['FP0057','FP0053']
    fixed_rate_funder = ['FP0046', 'FP0047']
    if funder_id in zero_intrate_funder:
        return "Zero"
    elif funder_id in notzero_intrate_funder:
        return "Main"
    elif funder_id in fixed_rate_funder:
        return "Fixed"
    else:
        return "Main"
#———————Rate Type settings: Rate
def get_rate_type(df):
    rate_info = str(df.loc[(df["field"] == "Interest Rate (% p.a.)") & (df["section"] == "SME Information"), "value"].iloc[0]).lower()
    if "sofr" in rate_info:
        return "SOFR+"
    elif "hibor" in rate_info:
        return "HIBOR+"
    else:
        return "Fixed"
#———————Drawdown ID settings: Product
def get_prdtype(df):
    drawdown_id = str(df.loc[(df["field"] == "Drawdown ID") & (df["section"] == "Payment Details"), "value"].iloc[0])
    zero_overdue = ['-COS-PL','-COSB-PL','-VEH-PL','-3CP-PL','PLCOS','PLCOS','PLPV','PL3C','NSDPL']#nooverdue
    rfpo_code = ['-IMP-RF','-IMP-PO','-LOG-RF']#RFPO
    if any(code in drawdown_id for code in zero_overdue):
        return "PL-novd"
    if any(code in drawdown_id for code in rfpo_code) or drawdown_id.startswith(("F-", "P-")):
        return "RFPO"
    else:
        return "Regular"