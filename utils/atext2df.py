import pandas as pd
import re

def parse_lms_to_df(raw_input):
    # 按 section 分割
    sections = re.split(r'\n(?=[A-Z][A-Za-z ]+\n)', raw_input)

    # 初始化 DataFrame
    df = pd.DataFrame(columns=['field', 'value', 'section'])

    # 逐个 section 处理
    for section in sections:
        lines = section.strip().split('\n')
        title = lines[0].strip()
        content = [line.split('\t') for line in lines[1:]]
        tempdf = pd.DataFrame(content, columns=['field', 'value'])
        tempdf['section'] = title
        df = pd.concat([df, tempdf], ignore_index=True)

    # 定义处理函数
    def process_value(field, value):
        if pd.isna(value) or value == '':
            return None
        field_lower = field.lower()
        if 'date' in field_lower:
            return pd.to_datetime(value, dayfirst=True, errors='coerce')
        elif 'rate' in field_lower:
            try:
                return float(value)
            except:
                return value
        elif 'day' in field_lower:
            try:
                return int(value)
            except:
                return None
        else:
            if isinstance(value, str) and '.' in value:
                try:
                    return float(value.replace(',', ''))
                except:
                    return value
            return value

    df.loc[(df["field"] == "Others") & (df["section"] == "Surcharge Items"), "value"] = pd.to_numeric(df.loc[(df["field"] == "Others") & (df["section"] == "Surcharge Items"), "value"])
    df['value'] = df.apply(lambda row: process_value(row['field'], row['value']), axis=1)


    return df


def generate_approval_dataframe(df, today, nature_input,transfer_acc, maker_name):
    approval_data = {
        "Date": today,
        "Repayment Date": [df.loc[(df["field"] == "Repayment Date") & (df["section"] == "Payment Details"), "value"].iloc[0]],
        "Drawdown ID": [df.loc[(df["field"] == "Drawdown ID") & (df["section"] == "Payment Details"), "value"].iloc[0]],
        "Nature": nature_input,
        "Funder Code": [df.loc[(df["field"] == "Funder ID") & (df["section"] == "Funder Information"), "value"].iloc[0]],
        "Currency": [df.loc[(df["field"] == "Repayment Currency") & (df["section"] == "Payment Details"), "value"].iloc[0]],
        "Principal": [df.loc[(df["field"] == "Repayment") & (df["section"] == "Funder Transaction"), "value"].iloc[0]],
        "Interest": [df.loc[(df["field"] == "Interest") & (df["section"] == "Funder Transaction"), "value"].iloc[0]],
        "Platform Fee": [df.loc[(df["field"] == "Platform Fee") & (df["section"] == "Funder Transaction"), "value"].iloc[0] * -1],
        "Spreading": [df.loc[(df["field"] == "FundPark Spreading") & (df["section"] == "FundPark Transaction"), "value"].iloc[0]],
        "Total Amount": [df.loc[(df["field"] == "Total Allocation") & (df["section"] == "Funder Transaction"), "value"].iloc[0]],
        "Sub": [df.loc[(df["field"] == "Bank Charge") & (df["section"] == "Payment Details"), "value"].iloc[0]],
        "Transfer Acc": [transfer_acc],
        "CSV": "",
        "Maker": maker_name,
        "Checker": "",
        "Approver": "",
        "Note": ""
    }
    syspreview_df = pd.DataFrame(approval_data)

    return syspreview_df



def process_email_data(text,today,nature_input,transfer_acc,maker_name):
    # Split according to the title number
    sections = text.split('\n')
    fp2_parsed_data = {}
    current_section = None

    for line in sections:
        if line.startswith(('1. ', '2. ', '3. ', '4. ', '5. ')):
            current_section = line.strip()
            fp2_parsed_data[current_section] = {}
        elif current_section:
            key_value = line.split('\t')
            if len(key_value) == 2:
                key = key_value[0].strip()
                value = key_value[1].strip()
                fp2_parsed_data[current_section][key] = value
    
        # Convert the parsed data dictionary to a pandas DataFrame

    # 构建目标格式的 DataFrame
    data = {
        "Date": [today],
        "Repayment Date": [fp2_parsed_data["1. Repayment Details"]["Repayment Date"]],
        "Trade Code": [fp2_parsed_data["1. Repayment Details"]["Trade Code"]],
        "Nature": [nature_input],
        "Funder Code": [fp2_parsed_data["2. Settlement to Funder"]["Funder sub account no"]],
        "Currency": [fp2_parsed_data["1. Repayment Details"]["Payment Currency"]],
        "Principal": [fp2_parsed_data["2. Settlement to Funder"]["Settled Loan Amount"]],
        "Interest": [fp2_parsed_data["2. Settlement to Funder"]["Settled Interest"]],
        "Platform Fee": [fp2_parsed_data["2. Settlement to Funder"]["Settled PF"]],
        "Spreading": [fp2_parsed_data["3. FundPark Allocation"]["FundPark Allocation Amount"]],
        "Total Amount": [fp2_parsed_data["1. Repayment Details"]["Actual Received Amount"]],
        "Sub": [""],
        "Transfer Acc": [transfer_acc],
        "CSV": [""],
        "Maker": [maker_name],
        "Checker":[""],
        "Approver":["N/A"]
    }

    syspreview_df= pd.DataFrame(data)


    return syspreview_df