import streamlit as st

def extract_and_validate(df, fundertype, ratetype, sme_interest, overdue_interest, funder_interest, spreading):
    valid_threshold = 0.02
    warnings = []
    # Extract values from df
    funderint_sys = df.loc[(df["field"] == "Interest") & (df["section"] == "Funder Transaction"), "value"].iloc[0]
    spreading_sys = df.loc[(df["field"] == "FundPark Spreading") & (df["section"] == "FundPark Transaction"), "value"].iloc[0]
    recieved_sys = df.loc[(df["field"] == "Total Allocation") & (df["section"] == "Funder Transaction"), "value"].iloc[0]
    rtb_sys = df.loc[(df["field"] == "Return to borrower") & (df["section"] == "SME Transaction"), "value"].iloc[0]
    smeint_sys = df.loc[(df["field"] == "Interest") & (df["section"] == "SME Transaction"), "value"].iloc[0]
    smeod_sys = df.loc[(df["field"] == "Overdue Interest") & (df["section"] == "SME Transaction"), "value"].iloc[0]

    principal_amount = df.loc[(df["field"] == "Repayment") & (df["section"] == "Funder Transaction"), "value"].iloc[0]
    outstanding_principal = df.loc[(df["field"] == "Outstanding Principal") & (df["section"] == "SME Transaction"), "value"].iloc[0]
    platform_fee = df.loc[(df["field"] == "Platform Fee") & (df["section"] == "Funder Transaction"), "value"].iloc[0]

    # Condition checks
    if outstanding_principal - principal_amount < 10 and outstanding_principal - principal_amount > 0.01:
        warnings.append("⚠️ Fully settle failed: outstanding_principal - principal_amount < 10")

    left = principal_amount + funderint_sys - platform_fee + spreading_sys
    right = recieved_sys
    if abs(left - right)>0.001:
        warnings.append(f"⚠️ Condition failed: cash flow mismatch — left side {left:.2f} ≠ right side {right:.2f}")

    if rtb_sys != 0:
        warnings.append(f"⚠️ Condition failed: rtb_sys should be 0, but is {rtb_sys}")

    if fundertype == "Main" and smeint_sys == 0:
        warnings.append("⚠️ Funder code violation: funder type is 'Main' but SME interest is 0 — main funders are expected to earn interest.")

    if fundertype == "Fixed" and ratetype != "Fixed":
        warnings.append("⚠️ Funder code violation: funder type is 'Fixed' but rate type is not 'Fixed' — this is inconsistent with fixed-rate funder logic.")

    if fundertype == "Zero" and smeint_sys != 0:
        warnings.append(f"⚠️ Funder code violation: funder type is 'Zero' but SME interest is {smeint_sys} — zero-interest funders should not earn interest.")

    sme_err = abs(sme_interest + overdue_interest - smeint_sys - smeod_sys)
    funder_err = abs(funder_interest - funderint_sys)
    spreading_err = abs(spreading - spreading_sys)

    def check_differences(err, threshold, label):
        status = "ok" if err < threshold else "problem"
        st.write(f"{label} {status}: {round(err,2)}")
    subcol1, subcol2, subcol3 = st.columns([1, 1, 1])
    with subcol1:
        check_differences(sme_err, valid_threshold, "SME")
    with subcol2:
        check_differences(funder_err, valid_threshold, "Funder")
    with subcol3:
        check_differences(spreading_err, valid_threshold, "Spreading")
    maxerr = max(sme_err, funder_err, spreading_err)
    status = "ok" if maxerr < valid_threshold else "problem"
    checker = f"{status}: {maxerr}"
    print(checker)

    return warnings, checker