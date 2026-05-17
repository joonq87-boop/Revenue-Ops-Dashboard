import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import os
import json
import requests
import feedparser
from datetime import datetime, timedelta
from google import genai
import random

st.set_page_config(page_title="Normality Revenue Optimizer", page_icon="⚡", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif; background: #f8f9fb; }
    .tct-header { background:linear-gradient(135deg,#0c1222 0%,#162040 50%,#1a2a52 100%); border-radius:16px; padding:1.5rem 2rem; margin-bottom:1.25rem; display:flex; justify-content:space-between; align-items:center; box-shadow:0 4px 24px rgba(10,22,40,0.12); }
    .tct-title { color:white; font-size:1.5rem; font-weight:700; letter-spacing:-0.02em; } .tct-subtitle { color:rgba(148,163,184,0.9); font-size:0.72rem; letter-spacing:0.12em; text-transform:uppercase; margin-top:0.2rem; font-weight:500; }
    .tct-badge { background:linear-gradient(135deg,#16a34a,#22c55e); color:white; font-size:0.68rem; font-weight:600; padding:5px 14px; border-radius:20px; letter-spacing:0.03em; }
    .tct-currency { background:rgba(255,255,255,0.08); color:rgba(255,255,255,0.85); font-size:0.78rem; padding:5px 14px; border-radius:8px; border:1px solid rgba(255,255,255,0.1); backdrop-filter:blur(8px); font-weight:500; }
    .metric-card { background:white; border:1px solid rgba(226,232,240,0.8); border-radius:14px; padding:1.15rem 1.4rem; transition:box-shadow 0.2s,transform 0.15s; }
    .metric-card:hover { box-shadow:0 2px 12px rgba(0,0,0,0.04); transform:translateY(-1px); }
    .metric-card-dark { background:linear-gradient(135deg,#0c1222 0%,#1a2d4d 100%); border:none; border-radius:14px; padding:1.15rem 1.4rem; box-shadow:0 4px 20px rgba(10,22,40,0.10); }
    .metric-card-dark .metric-label { color:rgba(148,163,184,0.85); } .metric-card-dark .metric-value { color:white; }
    .metric-card-green { border-left:3px solid #16a34a; } .metric-card-red { border-left:3px solid #dc2626; }
    .metric-card-amber { border-left:3px solid #f59e0b; } .metric-card-blue { border-left:3px solid #0369a1; }
    .metric-label { font-size:0.68rem; font-weight:600; letter-spacing:0.1em; text-transform:uppercase; color:#64748b; margin-bottom:0.4rem; }
    .metric-value { font-size:1.65rem; font-weight:700; color:#0f172a; line-height:1; font-family:'JetBrains Mono',monospace; letter-spacing:-0.02em; }
    .metric-delta { font-size:0.76rem; margin-top:0.3rem; font-weight:500; }
    .metric-delta.good { color:#16a34a; } .metric-delta.bad { color:#dc2626; } .metric-delta.neutral { color:#64748b; }
    .mex { font-size:0.65rem; color:#94a3b8; margin-top:0.45rem; border-top:1px solid #f1f5f9; padding-top:0.4rem; line-height:1.45; }
    .msrc { font-size:0.58rem; color:#bdc5d1; line-height:1.3; }
    .section-card { background:white; border:1px solid rgba(226,232,240,0.7); border-radius:16px; padding:1.6rem; margin-bottom:1rem; box-shadow:0 1px 3px rgba(0,0,0,0.02); }
    .section-title { font-size:0.76rem; font-weight:600; letter-spacing:0.1em; text-transform:uppercase; color:#475569; margin-bottom:1rem; padding-bottom:0.75rem; border-bottom:1px solid #f1f5f9; }
    .risk-badge { display:inline-block; padding:3px 10px; border-radius:20px; font-size:0.7rem; font-weight:600; letter-spacing:0.02em; }
    .risk-high { background:#fef2f2; color:#b91c1c; } .risk-med { background:#fffbeb; color:#92400e; } .risk-low { background:#f0fdf4; color:#166534; }
    .risk-why { font-size:0.7rem; color:#94a3b8; font-style:italic; margin-top:0.25rem; }
    .insight-row { display:flex; align-items:flex-start; gap:0.75rem; padding:0.75rem 0; border-bottom:1px solid #f1f5f9; font-size:0.9rem; }
    .insight-row:last-child { border-bottom:none; }
    .progress-bar-bg { background:#f1f5f9; border-radius:6px; height:7px; width:100%; margin-top:6px; }
    .progress-bar-fill { height:7px; border-radius:6px; }
    .news-card { background:#f8fafc; border:1px solid rgba(226,232,240,0.6); border-radius:12px; padding:0.9rem 1rem; margin-bottom:0.6rem; }
    .news-tag { display:inline-block; font-size:0.68rem; font-weight:600; padding:2px 9px; border-radius:20px; margin-right:4px; background:#eff6ff; color:#1d4ed8; }
    .info-box { background:linear-gradient(135deg,#eff6ff,#f0f9ff); border:1px solid #bfdbfe; border-radius:12px; padding:0.85rem 1.1rem; font-size:0.82rem; color:#1e40af; margin-bottom:0.75rem; }
    .module-card { background:white; border:1px solid rgba(226,232,240,0.7); border-radius:14px; padding:1.1rem; text-align:center; transition:box-shadow 0.2s; }
    .module-card:hover { box-shadow:0 2px 12px rgba(0,0,0,0.04); }
    .mod-explain { font-size:0.62rem; color:#94a3b8; margin-top:0.3rem; line-height:1.3; }
    .agent-card { background:#f8fafc; border-left:3px solid #0369a1; border-radius:0 12px 12px 0; padding:0.9rem 1rem; margin-bottom:0.6rem; }
    .agent-card.high { border-left-color:#dc2626; } .agent-card.medium { border-left-color:#f59e0b; } .agent-card.low { border-left-color:#16a34a; }
    .upload-hint { background:linear-gradient(135deg,#f8fafc,#f1f5f9); border:1.5px dashed #cbd5e1; border-radius:14px; padding:2rem; text-align:center; color:#64748b; font-size:0.88rem; }
    .stButton > button { background:linear-gradient(135deg,#0c1222,#1a2a52); color:white; border:none; border-radius:10px; padding:0.55rem 1.4rem; font-family:'Inter',sans-serif; font-size:0.88rem; font-weight:600; letter-spacing:0.01em; transition:all 0.2s; box-shadow:0 2px 8px rgba(10,22,40,0.12); }
    .stButton > button:hover { background:linear-gradient(135deg,#162040,#233568); transform:translateY(-1px); box-shadow:0 4px 16px rgba(10,22,40,0.18); }
    .var-card { background:white; border:1px solid rgba(226,232,240,0.7); border-radius:10px; padding:0.75rem 1rem; margin-bottom:0.5rem; }
    .var-label { font-size:0.85rem; font-weight:600; color:#0f172a; } .var-badge { font-size:0.63rem; font-weight:600; padding:2px 8px; border-radius:10px; background:#eff6ff; color:#1d4ed8; float:right; }
    .var-row { display:flex; justify-content:space-between; font-size:0.82rem; margin-top:0.3rem; }
    .var-pos { color:#16a34a; font-family:'JetBrains Mono',monospace; font-weight:600; } .var-neg { color:#dc2626; font-family:'JetBrains Mono',monospace; font-weight:600; }
    .cp-table { width:100%; border-collapse:separate; border-spacing:0; font-size:0.84rem; }
    .cp-table th { text-align:left; font-size:0.7rem; font-weight:600; text-transform:uppercase; letter-spacing:0.08em; color:#64748b; padding:0.6rem 0.75rem; border-bottom:2px solid #e2e8f0; }
    .cp-table td { padding:0.55rem 0.75rem; border-bottom:1px solid #f1f5f9; font-family:'JetBrains Mono',monospace; font-size:0.8rem; }
    .cp-table tr:hover td { background:#f8fafc; }
    .cp-green { color:#16a34a; } .cp-red { color:#dc2626; }
    .dash-nav { display:flex; gap:6px; margin-bottom:1.25rem; flex-wrap:wrap; }
    .dash-nav-btn { padding:8px 18px; border-radius:10px; font-size:0.82rem; font-weight:600; cursor:pointer; border:1px solid transparent; transition:all 0.2s; letter-spacing:0.01em; }
    .dash-nav-btn.active { background:linear-gradient(135deg,#0c1222,#1a2a52); color:white; box-shadow:0 2px 8px rgba(10,22,40,0.15); }
    .dash-nav-btn.inactive { background:white; color:#475569; border-color:#e2e8f0; }
    .dash-nav-btn.inactive:hover { background:#f8fafc; border-color:#cbd5e1; }
    .stTabs [data-baseweb="tab-list"] { gap:4px; background:transparent; }
    .stTabs [data-baseweb="tab"] { font-family:'Inter',sans-serif; font-size:0.82rem; font-weight:600; border-radius:10px; padding:8px 16px; color:#475569; }
    .stTabs [data-baseweb="tab"][aria-selected="true"] { background:linear-gradient(135deg,#0c1222,#1a2a52); color:white; }
    .stTabs [data-baseweb="tab-highlight"] { display:none; }
    .stTabs [data-baseweb="tab-border"] { display:none; }
    .stDownloadButton > button { background:white; color:#0c1222; border:1px solid #e2e8f0; border-radius:10px; font-weight:600; font-size:0.82rem; }
    .stDownloadButton > button:hover { background:#f8fafc; border-color:#cbd5e1; }
    div[data-testid="stExpander"] { border:1px solid rgba(226,232,240,0.7); border-radius:14px; overflow:hidden; }
    #MainMenu { visibility:hidden; } footer { visibility:hidden; }
    .stSelectbox > div > div { border-radius:10px; }
    .stNumberInput > div > div > input { border-radius:10px; }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def get_client():
    key = os.environ.get("GEMINI_API_KEY")
    if not key: st.error("GEMINI_API_KEY not found."); st.stop()
    return genai.Client(api_key=key)
client = get_client(); MODEL = "gemini-2.5-flash"

REGIONS = {"Indonesia":{"geo":"ID","worldbank":"IDN","currency":"IDR","fx_rate":15800,"symbol":"Rp"},"Thailand":{"geo":"TH","worldbank":"THA","currency":"THB","fx_rate":34.5,"symbol":"฿"},"Vietnam":{"geo":"VN","worldbank":"VNM","currency":"VND","fx_rate":25400,"symbol":"₫"},"Malaysia":{"geo":"MY","worldbank":"MYS","currency":"MYR","fx_rate":4.45,"symbol":"RM"},"Philippines":{"geo":"PH","worldbank":"PHL","currency":"PHP","fx_rate":56.8,"symbol":"₱"},"Singapore":{"geo":"SG","worldbank":"SGP","currency":"SGD","fx_rate":1.34,"symbol":"S$"}}
CURRENCIES = {"USD":{"rate":1,"symbol":"$","label":"USD ($)"}}
for rn,rd in REGIONS.items(): CURRENCIES[rd["currency"]]={"rate":rd["fx_rate"],"symbol":rd["symbol"],"label":f'{rd["currency"]} ({rd["symbol"]})'}
REGION_CUSTOMERS = {"Indonesia":["Indomaret","Alfamart","Hero Supermarket","Ranch Market","Lotte Mart ID","Carrefour ID"],"Thailand":["CP ALL 7-Eleven","Big C","Tesco Lotus","Makro TH","Tops Market","Villa Market"],"Vietnam":["Vinmart","Co.opmart","Bach Hoa Xanh","Big C VN","Lotte Mart VN","Circle K VN"],"Malaysia":["Lotus's MY","AEON Malaysia","Guardian MY","Watsons MY","Parkson","Cold Storage MY"],"Philippines":["SM Supermarket","Puregold","Robinsons","Mercury Drug","7-Eleven PH","S&R Members"],"Singapore":["FairPrice","Cold Storage SG","Giant SG","Sheng Siong","Guardian SG","Watsons SG"]}
INDUSTRIES = {"F&B / FMCG":{"keywords":["food","beverage","FMCG","consumer goods","grocery"],"worldbank_indicators":["NY.GDP.MKTP.KD.ZG","FP.CPI.TOTL.ZG"],"dso_benchmark":45,"inv_benchmark":40,"otif_benchmark":92,"cycle_benchmark":3},"Electronics Manufacturing":{"keywords":["electronics","semiconductor","manufacturing","supply chain"],"worldbank_indicators":["NY.GDP.MKTP.KD.ZG","NE.EXP.GNFS.ZS"],"dso_benchmark":50,"inv_benchmark":50,"otif_benchmark":88,"cycle_benchmark":5},"Medical / Healthcare":{"keywords":["medical","healthcare","pharmaceutical","hygiene"],"worldbank_indicators":["NY.GDP.MKTP.KD.ZG","SH.XPD.CHEX.GD.ZS"],"dso_benchmark":40,"inv_benchmark":45,"otif_benchmark":95,"cycle_benchmark":2},"Automotive / Industrial":{"keywords":["automotive","industrial","machinery","logistics"],"worldbank_indicators":["NY.GDP.MKTP.KD.ZG","NE.EXP.GNFS.ZS"],"dso_benchmark":55,"inv_benchmark":55,"otif_benchmark":90,"cycle_benchmark":4},"Retail / E-Commerce":{"keywords":["retail","e-commerce","online shopping","consumer"],"worldbank_indicators":["NY.GDP.MKTP.KD.ZG","FP.CPI.TOTL.ZG"],"dso_benchmark":30,"inv_benchmark":25,"otif_benchmark":95,"cycle_benchmark":2}}
RSS_FEEDS = {"Malaysia":[("The Star Business","https://www.thestar.com.my/rss/business"),("The Edge Malaysia","https://theedgemalaysia.com/feed")],"Singapore":[("Channel NewsAsia","https://www.channelnewsasia.com/rssfeeds/8395986"),("Straits Times","https://www.straitstimes.com/news/business/rss.xml")],"Vietnam":[("VnExpress Business","https://e.vnexpress.net/rss/business.rss")],"Indonesia":[("Jakarta Post","https://www.thejakartapost.com/feed/category/business")],"Thailand":[("Bangkok Post","https://www.bangkokpost.com/rss/data/business.xml")],"Philippines":[("Inquirer Business","https://business.inquirer.net/feed"),("Rappler Business","https://www.rappler.com/business/feed/")]}
WB_LABELS = {"NY.GDP.MKTP.KD.ZG":"GDP Growth (%)","FP.CPI.TOTL.ZG":"Inflation (CPI %)","NE.EXP.GNFS.ZS":"Exports (% GDP)","SH.XPD.CHEX.GD.ZS":"Health Exp (% GDP)"}
DIAGNOSTIC = {"Demand Forecasting":[{"q":"How is your demand forecast created?","opts":["Excel / spreadsheets only","ERP basic module","Dedicated planning tool","AI-assisted forecasting"],"key":"df_method"},{"q":"Do you track forecast accuracy (e.g. MAPE)?","opts":["No tracking at all","Occasionally reviewed","Monthly review","Real-time dashboard"],"key":"df_tracking"},{"q":"What % of customers provide usable forecast data?","opts":["Less than 25%","25-50%","50-75%","More than 75%"],"key":"df_customer_data"}],"Order Management":[{"q":"How are customer orders received?","opts":["Phone / Email only","Basic portal or fax","EDI integration","Fully automated multi-channel"],"key":"om_channel"},{"q":"Is order validation automated?","opts":["Fully manual checks","Partial validation rules","Mostly automated","Fully automated with exceptions"],"key":"om_validation"},{"q":"How often do customers amend orders?","opts":["Very frequently (>30%)","Often (15-30%)","Occasionally (5-15%)","Rarely (<5%)"],"key":"om_amendments"}],"Order Fulfilment & Logistics":[{"q":"Do you track OTIF (On-Time In-Full)?","opts":["Not tracked","Informally estimated","Formally tracked monthly","Real-time OTIF dashboard"],"key":"fl_otif"},{"q":"How is warehouse picking managed?","opts":["Paper-based / manual","Basic WMS","Advanced WMS with optimization","Automated / robotics-assisted"],"key":"fl_wms"},{"q":"Real-time shipment visibility?","opts":["No visibility","Partial (carrier websites)","Full tracking integration","Predictive ETA with alerts"],"key":"fl_visibility"}],"Billing & Revenue Mgmt":[{"q":"How are invoices triggered?","opts":["Manual creation","Semi-automated from ERP","Auto-generated on shipment","Touchless with compliance check"],"key":"br_invoicing"},{"q":"Discount / rebate governance?","opts":["No controls","Basic approval workflow","Rules-based engine","AI-governed with anomaly detection"],"key":"br_discount"},{"q":"Customer portal handling?","opts":["Not applicable","Manual uploads per customer","Partially automated","Fully automated per-customer rules"],"key":"br_portal"}],"Post-Sales & Financial Closure":[{"q":"How does AR team prioritize collections?","opts":["Ad hoc / reactive","First-in first-out","By invoice amount","Risk-based AI prioritization"],"key":"ps_collections"},{"q":"What % of receivables go past 90 days?","opts":["More than 20%","10-20%","5-10%","Less than 5%"],"key":"ps_aging"},{"q":"Cash application / reconciliation?","opts":["Fully manual","Partially automated","Mostly automated","Fully automated with AI matching"],"key":"ps_cash_app"}]}

def fmtc(value, ccy_code, compact=False):
    info = CURRENCIES.get(ccy_code, CURRENCIES["USD"]); converted = value * info["rate"]; sym = info["symbol"]
    if compact and abs(converted) >= 1_000_000: return f"{sym}{converted/1_000_000:,.1f}M"
    elif compact and abs(converted) >= 1_000: return f"{sym}{converted/1_000:,.1f}K"
    return f"{sym}{converted:,.0f}"

def mcard(label, val, delta, dcls, explain, source, card_cls="metric-card"):
    return f'<div class="{card_cls}"><div class="metric-label">{label}</div><div class="metric-value">{val}</div><div class="metric-delta {dcls}">{delta}</div><div class="mex">{explain}</div><div class="msrc">{source}</div></div>'

@st.cache_data(ttl=3600)
def fetch_news(region, industry):
    kws=[k.lower() for k in INDUSTRIES[industry]["keywords"]]; arts=[]
    for src,url in RSS_FEEDS.get(region,[]):
        try:
            feed=feedparser.parse(url)
            for e in feed.entries[:25]:
                t=e.get("title",""); s=e.get("summary",""); m=[k for k in kws if k in(t+" "+s).lower()]
                if m: arts.append({"title":t,"source":src,"published":e.get("published","")[:16],"keywords":m[:2]})
        except: pass
    return arts[:10]

@st.cache_data(ttl=86400)
def fetch_wb(region, industry):
    c=REGIONS[region]["worldbank"]; res={}
    for ind in INDUSTRIES[industry]["worldbank_indicators"]:
        try:
            r=requests.get(f"https://api.worldbank.org/v2/country/{c}/indicator/{ind}?format=json&mrv=5&per_page=5",timeout=8)
            if r.status_code==200:
                d=r.json()
                if len(d)>1 and d[1]:
                    s=[{"year":x["date"],"value":round(x["value"],2)} for x in d[1] if x["value"] is not None]
                    if s: res[WB_LABELS.get(ind,ind)]=sorted(s,key=lambda x:x["year"])
        except: pass
    return res

@st.cache_data(ttl=3600)
def fetch_gt(keywords, region):
    geo=REGIONS[region]["geo"]
    try:
        from pytrends.request import TrendReq
        pt=TrendReq(hl='en-US',tz=480,timeout=(10,25)); kws=keywords[:3]; pt.build_payload(kws,timeframe='today 1-m',geo=geo)
        df=pt.interest_over_time()
        if df.empty: return {"error":"No data.","data":{}}
        df=df.drop(columns=["isPartial"],errors="ignore")
        return {"data":{k:[{"date":str(d.date()),"value":int(v)} for d,v in zip(df.index,df[k])] for k in kws if k in df.columns}}
    except ImportError: return {"error":"pytrends not installed.","data":{}}
    except Exception as e: return {"error":str(e),"data":{}}

def calc_demand(df):
    df=df.copy(); df["MAPE"]=(df["Actual_Units"]-df["Forecast_Units"]).abs()/df["Actual_Units"].replace(0,np.nan)*100
    df["Bias"]=(df["Actual_Units"]-df["Forecast_Units"])/df["Actual_Units"].replace(0,np.nan)*100; mape=df["MAPE"].mean(); otif=0
    if "Orders_Placed" in df.columns and "Orders_OTIF" in df.columns: otif=round((df["Orders_OTIF"].sum()/max(df["Orders_Placed"].sum(),1))*100,1)
    sku=df.groupby("SKU").agg(MAPE=("MAPE","mean"),Bias=("Bias","mean"),Accuracy=("MAPE",lambda x:max(0,100-x.mean()))).reset_index().round(1)
    mo=df.groupby("Month").agg(Actual=("Actual_Units","sum"),Forecast=("Forecast_Units","sum")).reset_index()
    mo["Variance"]=mo["Actual"]-mo["Forecast"]; mo["Variance_Pct"]=((mo["Actual"]-mo["Forecast"])/mo["Forecast"].replace(0,np.nan)*100).round(1)
    return {"accuracy":round(max(0,100-mape),1),"mape":round(mape,1),"bias":round(df["Bias"].mean(),1),"otif":otif,"sku":sku,"monthly":df,"variance":mo}

def calc_order_mgmt(df):
    return {"cycle":round(df["Order_Cycle_Days"].mean(),1) if "Order_Cycle_Days" in df.columns else 0,"err":round(df.get("Invoice_Errors",pd.Series([0]*len(df))).mean()*100,1),"disp":round(df.get("Disputed",pd.Series([0]*len(df))).mean()*100,1),"amend":round(df.get("Amendment_Flag",pd.Series([0]*len(df))).mean()*100,1) if "Amendment_Flag" in df.columns else 12.0}

def calc_fulfilment(df,industry):
    bi=INDUSTRIES[industry]
    return {"otif":round((df["OTIF_Flag"].mean()*100) if "OTIF_Flag" in df.columns else 85.0,1),"otif_bench":bi["otif_benchmark"],"ful_days":round(df["Fulfilment_Days"].mean() if "Fulfilment_Days" in df.columns else 0,1),"ful_bench":bi["cycle_benchmark"],"return_rate":round((df["Return_Flag"].mean()*100) if "Return_Flag" in df.columns else 3.0,1),"partial":round(100-(df["OTIF_Flag"].mean()*100 if "OTIF_Flag" in df.columns else 85.0),1)}

def calc_billing(df,industry):
    bench=INDUSTRIES[industry]["dso_benchmark"]; dso=df["DSO_Days"].mean(); err=df.get("Invoice_Errors",pd.Series([0]*len(df))).mean()*100; disp=df.get("Disputed",pd.Series([0]*len(df))).mean()*100; rev=df["Invoice_Amount_USD"].sum()
    ld=rev*0.018; ie=rev*(err/100)*0.025; dd=rev*(disp/100)*0.05; ed=rev*0.008
    cust=df.groupby("Customer")["DSO_Days"].mean().reset_index(); cust.columns=["Customer","Avg_DSO"]
    cust["Risk"]=cust["Avg_DSO"].apply(lambda x:"High" if x>bench*1.4 else("Medium" if x>bench*1.1 else "Low"))
    cf=pd.DataFrame()
    if "Invoice_Date" in df.columns and "Payment_Date" in df.columns:
        d2=df.copy(); d2["Pay_Month"]=pd.to_datetime(d2["Payment_Date"]).dt.strftime("%b")
        inf=d2.groupby("Pay_Month")["Invoice_Amount_USD"].sum().reset_index(); inf.columns=["Month","Inflow"]
        inf["Outflow"]=(inf["Inflow"]*np.random.uniform(0.65,0.85,len(inf))).round(0); inf["Net"]=inf["Inflow"]-inf["Outflow"]; cf=inf
    rf=pd.DataFrame()
    if "Invoice_Date" in df.columns:
        d3=df.copy(); d3["Week"]=pd.to_datetime(d3["Invoice_Date"]).dt.isocalendar().week.astype(int)
        w=d3.groupby("Week")["Invoice_Amount_USD"].sum().reset_index(); w.columns=["Week","Actual"]
        w["Predicted"]=w["Actual"]*np.random.uniform(0.95,1.08,len(w)); w["Variance"]=w["Actual"]-w["Predicted"]
        w["Var_Pct"]=((w["Variance"]/w["Predicted"])*100).round(1); rf=w.tail(8).reset_index(drop=True)
    return {"dso":round(dso,1),"bench":bench,"gap":round(dso-bench,1),"err":round(err,1),"disp":round(disp,1),"rev":round(rev,0),"leak_total":round(ld+ie+dd+ed,0),"leak_disc":round(ld,0),"leak_inv":round(ie,0),"leak_disp":round(dd,0),"leak_ded":round(ed,0),"cust":cust.sort_values("Avg_DSO",ascending=False).round(1),"cashflow":cf,"recv_forecast":rf}

def calc_post_sales(df,industry,inv_days,dpo):
    dso=df["DSO_Days"].mean(); bd=INDUSTRIES[industry]["dso_benchmark"]; ccc=dso+inv_days-dpo; bc=bd+INDUSTRIES[industry]["inv_benchmark"]-30
    gap=ccc-bc; score=max(0,min(100,round(100-(gap/max(bc,1))*50)))
    aging={"current":round((df["DSO_Days"]<=30).mean()*100,1),"30d":round(((df["DSO_Days"]>30)&(df["DSO_Days"]<=60)).mean()*100,1),"60d":round(((df["DSO_Days"]>60)&(df["DSO_Days"]<=90)).mean()*100,1),"90d":round((df["DSO_Days"]>90).mean()*100,1)}
    ded=df["Deduction_USD"].sum() if "Deduction_USD" in df.columns else 0
    cp=[]
    if "Payment_Date" in df.columns:
        d4=df.copy(); d4["Payment_Date"]=pd.to_datetime(d4["Payment_Date"]); today=d4["Payment_Date"].max()-timedelta(days=30)
        for d in range(1,31):
            dt=today+timedelta(days=d); di=d4[d4["Payment_Date"].dt.date==dt.date()]["Invoice_Amount_USD"].sum()
            do=di*np.random.uniform(0.3,0.7) if di>0 else np.random.uniform(500,8000)
            cp.append({"Date":dt.strftime("%b %d"),"Inflow":round(di,0),"Outflow":round(do,0),"Net":round(di-do,0)})
    return {"ccc":round(ccc,1),"bench":round(bc,1),"dso":round(dso,1),"inv":inv_days,"dpo":dpo,"gap":round(gap,1),"score":score,"health":"Good" if score>=70 else "At Risk" if score>=45 else "Critical","aging":aging,"deductions":round(ded,0),"cash_pos":cp}

def calc_module_scores(dm,om,fl,bl,ps,diag):
    data={"Demand Forecasting":min(100,round(dm["accuracy"]*0.7+max(0,20-abs(dm["bias"]))*1.5)),"Order Management":max(0,min(100,round(100-om["err"]*5-om["disp"]*3-om["amend"]*0.5))),"Order Fulfilment & Logistics":max(0,min(100,round(fl["otif"]*0.8+max(0,10-fl["return_rate"])*2))),"Billing & Revenue Mgmt":max(0,min(100,round(100-bl["err"]*8-bl["disp"]*4))),"Post-Sales & Financial Closure":ps["score"]}
    return {m:round(data[m]*0.6+diag.get(m,50)*0.4) for m in data}

def calc_customer_ltv(df, industry):
    """Customer LTV Engine: combines revenue, margin, payment behaviour, dispute rate, tenure into LTV score."""
    cust = df.groupby("Customer").agg(
        total_revenue=("Invoice_Amount_USD", "sum"),
        order_count=("Order_ID", "count"),
        avg_dso=("DSO_Days", "mean"),
        dispute_rate=("Disputed", lambda x: x.mean() * 100 if "Disputed" in df.columns else 0),
        return_rate=("Return_Flag", lambda x: x.mean() * 100 if "Return_Flag" in df.columns else 0),
        avg_order_value=("Invoice_Amount_USD", "mean"),
        deductions=("Deduction_USD", "sum") if "Deduction_USD" in df.columns else ("Invoice_Amount_USD", lambda x: 0),
    ).reset_index()
    bench_dso = INDUSTRIES[industry]["dso_benchmark"]
    if "Order_Date" in df.columns and "Payment_Date" in df.columns:
        tenure = df.groupby("Customer").apply(lambda g: (pd.to_datetime(g["Payment_Date"]).max() - pd.to_datetime(g["Order_Date"]).min()).days).reset_index()
        tenure.columns = ["Customer", "tenure_days"]
        cust = cust.merge(tenure, on="Customer", how="left")
    else:
        cust["tenure_days"] = 365
    cust["tenure_months"] = (cust["tenure_days"] / 30).clip(lower=1).round(0).astype(int)
    cust["monthly_revenue"] = cust["total_revenue"] / cust["tenure_months"]
    cust["est_gross_margin"] = cust["total_revenue"] * 0.35
    cust["cost_to_serve"] = (cust["deductions"] + cust["total_revenue"] * (cust["dispute_rate"] / 100) * 0.05 + cust["total_revenue"] * (cust["return_rate"] / 100) * 0.15)
    cust["net_margin"] = cust["est_gross_margin"] - cust["cost_to_serve"]
    cust["net_margin_pct"] = (cust["net_margin"] / cust["total_revenue"].replace(0, np.nan) * 100).round(1)
    dso_score = (100 - ((cust["avg_dso"] - bench_dso).clip(lower=0) / bench_dso * 60)).clip(0, 100)
    dispute_score = (100 - cust["dispute_rate"] * 12).clip(0, 100)
    frequency_score = (cust["order_count"] / cust["order_count"].max() * 100).clip(0, 100)
    revenue_score = (cust["total_revenue"] / cust["total_revenue"].max() * 100).clip(0, 100)
    cust["health_score"] = (revenue_score * 0.15 + frequency_score * 0.15 + dso_score * 0.40 + dispute_score * 0.30).round(0).astype(int)
    # Hard penalty: if DSO > 2x benchmark or dispute > 15%, cap health at 35
    cust.loc[cust["avg_dso"] > bench_dso * 1.8, "health_score"] = cust.loc[cust["avg_dso"] > bench_dso * 1.8, "health_score"].clip(upper=35)
    cust.loc[cust["dispute_rate"] > 12, "health_score"] = cust.loc[cust["dispute_rate"] > 12, "health_score"].clip(upper=35)
    cust["ltv_12m"] = (cust["monthly_revenue"] * 12 * 0.35 - cust["cost_to_serve"] / cust["tenure_months"] * 12).round(0)
    cust["churn_risk"] = cust["health_score"].apply(lambda x: "High" if x < 40 else "Medium" if x < 65 else "Low")
    def assign_segment(r):
        if r["health_score"] < 40: return "Monitor"
        if r["health_score"] < 55: return "At Risk"
        if r["ltv_12m"] > cust["ltv_12m"].quantile(0.75) and r["health_score"] >= 65: return "Strategic"
        if r["health_score"] >= 60: return "Growth"
        return "At Risk"
    cust["segment"] = cust.apply(assign_segment, axis=1)
    return cust.sort_values("ltv_12m", ascending=False).round(1)

def calc_cash_app_simulation(df):
    """Auto Cash Application simulation: matches payments to invoices using amount, identity, and pattern."""
    if "Invoice_Amount_USD" not in df.columns or "Customer" not in df.columns:
        return {"match_rate": 0, "auto_matched": 0, "manual_review": 0, "unmatched": 0, "items": []}
    np.random.seed(42)
    n = min(len(df), 30)
    sample = df.sample(n=n, random_state=42).copy()
    sample["Remittance_Amount"] = sample["Invoice_Amount_USD"] * np.random.choice([1.0, 1.0, 1.0, 0.98, 0.95, 1.02], n)
    sample["Remittance_Amount"] = sample["Remittance_Amount"].round(2)
    sample["Amount_Match"] = (abs(sample["Invoice_Amount_USD"] - sample["Remittance_Amount"]) / sample["Invoice_Amount_USD"] < 0.03)
    sample["Identity_Match"] = np.random.choice([True, True, True, True, False], n)
    sample["Pattern_Match"] = np.random.choice([True, True, True, False, False], n)
    sample["Confidence"] = (sample["Amount_Match"].astype(int) * 45 + sample["Identity_Match"].astype(int) * 35 + sample["Pattern_Match"].astype(int) * 20)
    sample["Match_Status"] = sample["Confidence"].apply(lambda c: "Auto-Matched" if c >= 80 else "Review Required" if c >= 45 else "Unmatched")
    sample["Match_Method"] = sample.apply(lambda r: "Amount + Identity + Pattern" if r["Confidence"] >= 80 else "Partial match — " + (", ".join(filter(None, ["amount" if r["Amount_Match"] else None, "identity" if r["Identity_Match"] else None, "pattern" if r["Pattern_Match"] else None])) or "no signal"), axis=1)
    auto = (sample["Match_Status"] == "Auto-Matched").sum()
    review = (sample["Match_Status"] == "Review Required").sum()
    unmatched = (sample["Match_Status"] == "Unmatched").sum()
    items = sample[["Order_ID", "Customer", "Invoice_Amount_USD", "Remittance_Amount", "Confidence", "Match_Status", "Match_Method"]].to_dict("records")
    return {"match_rate": round(auto / max(n, 1) * 100, 1), "auto_matched": int(auto), "manual_review": int(review), "unmatched": int(unmatched), "total": int(n), "items": items}

def calc_dispute_workflow(df):
    """CollectIQ Dispute Engine simulation: categorises, routes, and recommends resolution."""
    if "Disputed" not in df.columns:
        return {"total": 0, "categories": {}, "items": []}
    disputed = df[df["Disputed"] == 1].copy()
    if len(disputed) == 0:
        return {"total": 0, "categories": {}, "items": []}
    np.random.seed(42)
    categories = ["Pricing mismatch", "Quantity short", "Quality/damage", "Documentation error", "Duplicate invoice", "Unauthorised deduction"]
    disputed["Dispute_Category"] = np.random.choice(categories, len(disputed))
    severity_map = {"Pricing mismatch": "High", "Quantity short": "Medium", "Quality/damage": "High", "Documentation error": "Low", "Duplicate invoice": "Low", "Unauthorised deduction": "Medium"}
    disputed["Severity"] = disputed["Dispute_Category"].map(severity_map)
    resolution_map = {"Pricing mismatch": "Auto-pull PriceGuard contract rate; issue credit note if delta confirmed", "Quantity short": "Cross-check ShipmentTracker ePOD qty vs order; auto-credit if shortfall verified", "Quality/damage": "Route to quality team; pull ePOD photos; initiate ReturnFlow if confirmed", "Documentation error": "Auto-reissue with DocComplete validation; no revenue impact", "Duplicate invoice": "Auto-void duplicate; update AR immediately", "Unauthorised deduction": "Flag for commercial review; compare against contract terms in PriceGuard"}
    disputed["AI_Resolution"] = disputed["Dispute_Category"].map(resolution_map)
    status_choices = ["Auto-Resolved", "Auto-Resolved", "Pending Review", "Escalated"]
    disputed["Status"] = np.random.choice(status_choices, len(disputed))
    days_to_resolve = {"Auto-Resolved": np.random.randint(0, 2, len(disputed)), "Pending Review": np.random.randint(2, 7, len(disputed)), "Escalated": np.random.randint(7, 21, len(disputed))}
    disputed["Est_Days"] = disputed["Status"].apply(lambda s: np.random.choice(days_to_resolve.get(s, [5])))
    cat_counts = disputed["Dispute_Category"].value_counts().to_dict()
    items = disputed[["Order_ID", "Customer", "Invoice_Amount_USD", "Dispute_Category", "Severity", "AI_Resolution", "Status", "Est_Days"]].head(12).to_dict("records")
    auto_rate = round((disputed["Status"] == "Auto-Resolved").mean() * 100, 1)
    return {"total": len(disputed), "categories": cat_counts, "items": items, "auto_resolve_rate": auto_rate, "avg_days_before": 18, "avg_days_after": round(disputed["Est_Days"].mean(), 1)}

def generate_order_ingest_demo(region):
    """Simulates OrderIngest Hub processing: multi-channel orders parsed by LLM/OCR."""
    np.random.seed(42)
    custs = REGION_CUSTOMERS.get(region, REGION_CUSTOMERS["Singapore"])
    channels = ["Email PDF", "EDI X12", "WhatsApp Image", "Customer Portal", "Fax Scan", "Email (unstructured)"]
    statuses = ["Auto-Parsed", "Auto-Parsed", "Auto-Parsed", "Human Review", "AI Gap-Fill"]
    skus = ["SKU-FMCG-001", "SKU-FMCG-002", "SKU-FMCG-003", "SKU-ELEC-001", "SKU-MED-001"]
    orders = []
    for i in range(15):
        ch = random.choice(channels)
        confidence = random.randint(72, 99) if ch in ["EDI X12", "Customer Portal"] else random.randint(55, 92)
        status = "Auto-Parsed" if confidence >= 85 else "Human Review" if confidence >= 70 else "AI Gap-Fill"
        fields_extracted = random.randint(8, 12) if confidence >= 85 else random.randint(5, 8)
        fields_total = 12
        missing = [] if fields_extracted >= 11 else random.sample(["Delivery Date", "PO Reference", "Unit Price", "Ship-To Code", "Payment Terms"], min(3, fields_total - fields_extracted))
        orders.append({
            "po_id": f"PO-{2024000 + i}",
            "customer": random.choice(custs),
            "channel": ch,
            "sku_count": random.randint(1, 8),
            "amount_usd": round(random.uniform(3000, 85000), 2),
            "confidence": confidence,
            "status": status,
            "fields_extracted": fields_extracted,
            "fields_total": fields_total,
            "missing_fields": missing,
            "processing_time": f"{random.uniform(0.5, 3.5):.1f}s" if confidence >= 85 else f"{random.uniform(3, 15):.0f}s",
        })
    auto = sum(1 for o in orders if o["status"] == "Auto-Parsed")
    return {"orders": orders, "auto_rate": round(auto / len(orders) * 100, 1), "avg_confidence": round(np.mean([o["confidence"] for o in orders]), 1), "channels_active": len(set(o["channel"] for o in orders))}

def generate_invoice_demo(df, region):
    """BillingEngine simulation: auto-invoice trigger on shipment confirmation."""
    np.random.seed(42)
    custs = REGION_CUSTOMERS.get(region, REGION_CUSTOMERS["Singapore"])
    invoices = []
    for i in range(12):
        trigger = random.choice(["ePOD Confirmed", "ePOD Confirmed", "ePOD Confirmed", "Milestone Reached", "Consignment Threshold"])
        val_checks = ["Qty vs ePOD", "Price vs PriceGuard", "Tax compliance", "Doc requirements"]
        passed = random.sample(val_checks, k=random.randint(3, 4))
        failed = [c for c in val_checks if c not in passed]
        status = "Auto-Generated" if len(failed) == 0 else "Validation Hold"
        invoices.append({
            "invoice_id": f"INV-{2024100 + i}",
            "order_id": f"ORD-{1000 + i}",
            "customer": random.choice(custs),
            "amount_usd": round(random.uniform(5000, 75000), 2),
            "trigger": trigger,
            "checks_passed": passed,
            "checks_failed": failed,
            "status": status,
            "time_to_invoice": f"{random.uniform(0.1, 0.8):.1f} hrs" if status == "Auto-Generated" else f"{random.uniform(2, 24):.0f} hrs (manual review)",
            "before_time": f"{random.uniform(24, 96):.0f} hrs (manual process)"
        })
    auto = sum(1 for inv in invoices if inv["status"] == "Auto-Generated")
    return {"invoices": invoices, "auto_rate": round(auto / len(invoices) * 100, 1), "avg_time_after": round(np.mean([0.5 if inv["status"] == "Auto-Generated" else 12 for inv in invoices]), 1), "avg_time_before": 48}

def get_diag_scores(resp):
    sc={}
    for mod,qs in DIAGNOSTIC.items(): vals=[(resp.get(q["key"],0)+1)*25 for q in qs]; sc[mod]=round(sum(vals)/len(vals)) if vals else 50
    return sc

def get_executive_ai(dm,om,fl,bl,ps,ms,diag,region,industry,ccy):
    p=f"""Revenue Optimizer AI for {industry} in {region}. Currency: {ccy}. MODULE SCORES: {json.dumps(ms)}
DEMAND: Accuracy {dm['accuracy']}%, MAPE {dm['mape']}%, Bias {dm['bias']:+.1f}%, OTIF {dm['otif']}%
ORDER: Cycle {om['cycle']}d, Errors {om['err']}%, Disputes {om['disp']}%, Amendments {om['amend']}%
FULFILMENT: OTIF {fl['otif']}% (bench {fl['otif_bench']}%), Returns {fl['return_rate']}%
BILLING: DSO {bl['dso']}d (bench {bl['bench']}d), Leakage USD {bl['leak_total']:,.0f}
POST-SALES: CCC {ps['ccc']}d (bench {ps['bench']}d), Score {ps['score']}/100, AR>90d: {ps['aging']['90d']}%
MATURITY: {json.dumps(diag)}
Context: SEA CPG mid-market. Pain: non-binding forecasts, spreadsheet dependence, portal failures, manual rebates.
For each risk, include a 'why' field: 1 sentence explaining why this severity was assigned based on the data.
Return ONLY valid JSON: {{"overall_health":"Good|At Risk|Critical","health_score":<int>,"health_reason":"1 sentence explaining the score based on data",
"executive_summary":"3-4 sentence summary","top_risks":[{{"risk":"...","severity":"High|Medium|Low","impact":"...","module":"...","why":"1 sentence data-based reason for this severity"}}],
"quick_wins":[{{"action":"...","timeline":"...","expected_impact":"...","module":"..."}}],"forecast_insight":"...","o2c_insight":"...","wc_insight":"..."}}"""
    r=client.models.generate_content(model=MODEL,contents=p); t=r.text.strip().lstrip("```json").lstrip("```").rstrip("```").strip(); return json.loads(t)

def get_agent_simulation(dm,om,fl,bl,ps,ms,region,industry,ccy):
    p=f"""Revenue Optimizer AI agent for {industry} in {region}. Currency: {ccy}. Simulate 8 realistic interventions over 30 days.
DATA: Accuracy:{dm['accuracy']}%, OTIF:{dm['otif']}%, Cycle:{om['cycle']}d, Amendments:{om['amend']}%, Errors:{om['err']}%, OTIF:{fl['otif']}%, Returns:{fl['return_rate']}%, DSO:{bl['dso']}d(bench{bl['bench']}d), Leakage:USD{bl['leak_total']:,.0f}, CCC:{ps['ccc']}d, AR>90d:{ps['aging']['90d']}%
Return ONLY valid JSON: {{"interventions":[{{"day":1,"module":"...","severity":"High|Medium|Low","trigger":"...","action":"...","impact":"..."}}]}}"""
    r=client.models.generate_content(model=MODEL,contents=p); t=r.text.strip().lstrip("```json").lstrip("```").rstrip("```").strip(); return json.loads(t)

def get_demand_signals_ai(region,industry,news,wb,gt):
    nt="\n".join([f"- [{a['source']}] {a['title']}" for a in news[:8]]) or "None."
    wt="\n".join([f"- {l}: {s[-1]['value']} ({s[-1]['year']})" for l,s in wb.items() if s]) or "None."
    gtt="\n".join([f"- '{k}': avg {round(sum(p['value'] for p in s)/len(s),1)}/100" for k,s in gt.get("data",{}).items() if s]) or gt.get("error","N/A")
    p=f"""Demand AI for {industry} in {region}. Analyse ONLY data below. Cite sources.
NEWS: {nt}\nWORLD BANK: {wt}\nGOOGLE TRENDS: {gtt}
Return ONLY valid JSON: {{"demand_signals":[{{"signal":"...","source":"...","impact":"...","forecast_adjustment":"..."}}],"supply_risks":[{{"risk":"...","source":"...","severity":"High|Medium|Low","mitigation":"..."}}],"market_summary":"3 sentences citing sources"}}"""
    r=client.models.generate_content(model=MODEL,contents=p); t=r.text.strip().lstrip("```json").lstrip("```").rstrip("```").strip(); return json.loads(t)

def sample_demand():
    np.random.seed(42); skus=["SKU-FMCG-001","SKU-FMCG-002","SKU-FMCG-003","SKU-FMCG-004"]; rows=[]
    for yr in [2023,2024,2025,2026]:
        max_mo = 5 if yr == 2026 else 12
        months=pd.date_range(f"{yr}-01-01",periods=max_mo,freq="MS")
        err_scale={2023:0.14,2024:0.10,2025:0.08,2026:0.07}[yr]
        for sku in skus:
            base=np.random.randint(900,2800)
            sku_err = err_scale * 2.2 if sku == "SKU-FMCG-002" else err_scale
            sku_bias = -0.06 if sku == "SKU-FMCG-002" else 0.0
            for m in months:
                seasonal=0.10*np.sin((m.month-1)/12*2*np.pi)+0.05*np.sin((m.month-1)/12*4*np.pi)
                cny_bump=0.10 if m.month in [1,2] else 0
                a=int(base*(1+seasonal+cny_bump+np.random.normal(0,0.04))*(1+0.04*(yr-2023)))
                f=int(a*(1+sku_bias+np.random.normal(0,sku_err)))
                pl=max(10,int(a/np.random.randint(50,150))); ot_rate={2023:0.83,2024:0.87,2025:0.90,2026:0.92}[yr]
                ot=int(pl*np.random.uniform(ot_rate-0.04,min(ot_rate+0.04,0.98)))
                rows.append({"Month":m.strftime("%Y-%m"),"SKU":sku,"Actual_Units":a,"Forecast_Units":f,"Orders_Placed":pl,"Orders_OTIF":ot})
    return pd.DataFrame(rows)

def sample_o2c(region):
    np.random.seed(42); custs=REGION_CUSTOMERS.get(region,REGION_CUSTOMERS["Singapore"]); rows=[]
    oid=1000
    for yr in [2023,2024,2025,2026]:
        max_mo = 5 if yr == 2026 else 12
        dso_base={2023:52,2024:48,2025:44,2026:42}[yr]
        err_rate={2023:0.06,2024:0.04,2025:0.03,2026:0.025}[yr]
        disp_rate={2023:0.05,2024:0.035,2025:0.025,2026:0.02}[yr]
        amend_rate={2023:0.09,2024:0.07,2025:0.05,2026:0.04}[yr]
        for mo in range(1,max_mo+1):
            n_orders=random.randint(18,24)
            for _ in range(n_orders):
                cust = random.choice(custs)
                od=datetime(yr,mo,1)+timedelta(days=random.randint(0,min(27,28)))
                cd=random.randint(1,5); fd=random.randint(1,4)
                inv=od+timedelta(days=cd)
                # Guardian SG is a problem customer — slow payer, disputes, deductions
                if cust == "Guardian SG":
                    dso_jitter=int(np.random.normal(dso_base*1.6,dso_base*0.3))
                    dso_jitter=max(45,min(dso_jitter,150))
                    c_err = err_rate * 2.5
                    c_disp = disp_rate * 4.0
                    c_ded = 0.35
                    c_amend = amend_rate * 2.0
                else:
                    dso_jitter=int(np.random.normal(dso_base,dso_base*0.22))
                    dso_jitter=max(12,min(dso_jitter,110))
                    c_err = err_rate
                    c_disp = disp_rate
                    c_ded = 0.08
                    c_amend = amend_rate
                pay=inv+timedelta(days=dso_jitter)
                amt=round(random.uniform(5000,80000),2)
                rows.append({"Order_ID":f"ORD-{oid}","Customer":cust,"Order_Date":od.strftime("%Y-%m-%d"),"Invoice_Date":inv.strftime("%Y-%m-%d"),"Payment_Date":pay.strftime("%Y-%m-%d"),"Invoice_Amount_USD":amt,"DSO_Days":dso_jitter,"Order_Cycle_Days":cd,"Fulfilment_Days":fd,"Invoice_Errors":1 if random.random()<c_err else 0,"Disputed":1 if random.random()<c_disp else 0,"OTIF_Flag":1 if random.random()>0.06 else 0,"Return_Flag":1 if random.random()<0.04 else 0,"Amendment_Flag":1 if random.random()<c_amend else 0,"Deduction_USD":round(random.uniform(100,800) if random.random()<c_ded else 0,2),"Inventory_Days":42,"DPO_Days":32})
                oid+=1
    return pd.DataFrame(rows)

def sample_maturity(region="Singapore",industry="F&B / FMCG",currency="USD"):
    """Generate maturity assessment CSV — company doing well with a few specific gaps."""
    rows=[
        {"Parameter":"region","Value":region},{"Parameter":"industry","Value":industry},{"Parameter":"currency","Value":currency},
        {"Parameter":"df_method","Value":"2"},{"Parameter":"df_tracking","Value":"2"},{"Parameter":"df_customer_data","Value":"3"},
        {"Parameter":"om_channel","Value":"2"},{"Parameter":"om_validation","Value":"1"},{"Parameter":"om_amendments","Value":"3"},
        {"Parameter":"fl_otif","Value":"3"},{"Parameter":"fl_wms","Value":"2"},{"Parameter":"fl_visibility","Value":"3"},
        {"Parameter":"br_invoicing","Value":"1"},{"Parameter":"br_discount","Value":"2"},{"Parameter":"br_portal","Value":"3"},
        {"Parameter":"ps_collections","Value":"2"},{"Parameter":"ps_aging","Value":"3"},{"Parameter":"ps_cash_app","Value":"0"},
    ]
    return pd.DataFrame(rows)

def parse_maturity_csv(df):
    """Parse maturity CSV into region, industry, currency, diag_responses, inv_days, dpo_days."""
    params=dict(zip(df["Parameter"],df["Value"]))
    region=params.get("region","Singapore"); industry=params.get("industry","F&B / FMCG"); currency=params.get("currency","USD")
    diag={}; q_keys=["df_method","df_tracking","df_customer_data","om_channel","om_validation","om_amendments","fl_otif","fl_wms","fl_visibility","br_invoicing","br_discount","br_portal","ps_collections","ps_aging","ps_cash_app"]
    for k in q_keys: diag[k]=int(params.get(k,0))
    return region, industry, currency, diag

def get_available_years(df, date_col="Order_Date"):
    try:
        years = sorted(pd.to_datetime(df[date_col]).dt.year.unique().tolist(), reverse=True)
        labels = []
        for y in years:
            if y == 2026: labels.append("2026 YTD")
            else: labels.append(str(y))
        return ["Last 3 Years"] + labels
    except: return ["Last 3 Years"]

def get_demand_years(df):
    try:
        years = sorted(df["Month"].str[:4].unique().tolist(), reverse=True)
        labels = []
        for y in years:
            if y == "2026": labels.append("2026 YTD")
            else: labels.append(y)
        return ["Last 3 Years"] + labels
    except: return ["Last 3 Years"]

def filter_by_year(df, year, date_col="Order_Date"):
    if year == "Last 3 Years": return df
    yr = int(year.replace(" YTD",""))
    dc = pd.to_datetime(df[date_col])
    return df[dc.dt.year == yr]

def filter_demand_by_year(df, year):
    if year == "Last 3 Years": return df
    yr = year.replace(" YTD","")
    return df[df["Month"].str.startswith(yr)]

def scolor(s): return "#16a34a" if s>=70 else "#ea580c" if s>=45 else "#dc2626"

# Plain-English insights for each maturity question, keyed by (question_key, answer_index)
MATURITY_INSIGHTS = {
    "df_method": [
        "You're forecasting in spreadsheets — manual processes typically produce 25-40% error rates. ML-assisted forecasting can cut this in half.",
        "Your ERP gives you a baseline, but basic modules lack external signals. Adding context data (promotions, seasonality) could improve accuracy by 10-15%.",
        "You have dedicated planning tools — that puts you ahead of most SEA mid-market. The next step is layering in AI ensemble models.",
        "AI-assisted forecasting is best-in-class. Your tools are not the bottleneck."
    ],
    "df_tracking": [
        "You're not tracking forecast accuracy — you can't improve what you can't measure. Even monthly MAPE tracking would surface quick wins.",
        "Occasional reviews catch big misses but miss slow drift. Moving to monthly tracking would surface systematic bias earlier.",
        "Monthly reviews are solid practice. Real-time dashboards would let you catch deviations within the planning cycle, not after.",
        "Real-time accuracy tracking is best-in-class. Your visibility is not the bottleneck."
    ],
    "df_customer_data": [
        "Less than 25% of customers provide usable forecasts — you're essentially guessing demand. Even partial customer signals dramatically improve accuracy.",
        "25-50% customer data coverage leaves significant blind spots. Distributor portals could close the gap without heavy integration.",
        "50-75% coverage is strong. Focus on the top 20% of customers who drive 80% of volume to maximise signal quality.",
        "75%+ customer data coverage is excellent — your demand signal is not the bottleneck."
    ],
    "om_channel": [
        "Phone and email orders require manual re-keying — this is the #1 source of order errors. Every re-key is a potential dispute downstream.",
        "Basic portals reduce some manual entry, but format inconsistency still causes parsing errors. Unified ingestion is the fix.",
        "EDI integration eliminates most re-keying. The remaining gap is non-EDI channels (WhatsApp, email) that bypass the system.",
        "Fully automated multi-channel intake is best-in-class. Your order capture is not the bottleneck."
    ],
    "om_validation": [
        "Fully manual validation means errors reach the ERP — and cascade into wrong shipments, wrong invoices, and disputes.",
        "Partial validation catches some issues, but exceptions still slip through. Full ATP + credit + price validation would close the gap.",
        "Mostly automated validation is strong. Focus on the exception handling — the 5-10% that escapes automation causes outsized damage.",
        "Fully automated with exception routing is best-in-class. Your validation is not the bottleneck."
    ],
    "om_amendments": [
        "Over 30% amendment rate means your order process is being used as a draft system. Each amendment costs processing time and risks errors.",
        "15-30% amendments are common in SEA but still expensive. Order confirmation workflows with cut-off rules can reduce this significantly.",
        "5-15% amendments are within industry norm. Focus on reducing the ones that happen after production commitment — those are the costly ones.",
        "Below 5% amendments is excellent discipline — your change management is not the bottleneck."
    ],
    "fl_otif": [
        "If you're not tracking OTIF, you don't know if customers are getting what they ordered on time. This is the most basic fulfilment metric.",
        "Informal estimates give you a rough picture but can't identify root causes. Formal tracking by customer, SKU, and route reveals where to act.",
        "Monthly formal tracking is solid. Real-time OTIF dashboards would let you intervene on at-risk shipments before they become failures.",
        "Real-time OTIF tracking is best-in-class. Your fulfilment visibility is not the bottleneck."
    ],
    "fl_wms": [
        "Paper-based warehouse management limits pick accuracy and throughput. Even a basic WMS would reduce mispicks and speed up dispatch.",
        "Basic WMS handles tracking but not optimisation. Wave planning and route-optimised picking could improve throughput 15-20%.",
        "Advanced WMS with optimisation is strong. The next level is predictive allocation — pre-positioning stock based on forecast signals.",
        "Automated/robotics-assisted warehouse is best-in-class. Your warehouse operations are not the bottleneck."
    ],
    "fl_visibility": [
        "No shipment visibility means you can't proactively manage delivery exceptions. Customers find out about delays before you do.",
        "Partial visibility via carrier websites is reactive and fragmented. Integrated tracking across carriers gives you a single view.",
        "Full tracking integration is strong. Predictive ETA with proactive alerts would let you manage exceptions before customers escalate.",
        "Predictive ETA with alerts is best-in-class. Your logistics visibility is not the bottleneck."
    ],
    "br_invoicing": [
        "Manual invoice creation is the #1 cause of billing delays. Every day between shipment and invoice is a day added to DSO.",
        "Semi-automated from ERP helps, but the manual trigger step still adds 24-48 hours. Auto-trigger on ePOD confirmation would eliminate this.",
        "Auto-generated on shipment is strong. Adding compliance checks (price validation, tax, documentation) before release would reduce disputes.",
        "Touchless invoicing with compliance checks is best-in-class. Your billing speed is not the bottleneck."
    ],
    "br_discount": [
        "No discount controls means sales staff apply ad-hoc discounts with no governance — revenue leakage is systematic and invisible.",
        "Basic approval workflows catch some deviations, but retroactive approvals still slip through. Rules-based engines enforce at point of sale.",
        "Rules-based discount governance is strong. AI anomaly detection would flag unusual patterns (e.g., consistent max-discount on specific accounts).",
        "AI-governed discount controls are best-in-class. Your pricing discipline is not the bottleneck."
    ],
    "br_portal": [
        "No customer portal capability means all invoice submission is manual — this is acceptable for some industries but adds DSO for portal-dependent customers.",
        "Manual uploads per customer don't scale. Each portal has different rules, formats, and submission windows that staff must memorise.",
        "Partially automated portal handling reduces effort. Full automation with per-customer rule engines eliminates submission delays entirely.",
        "Fully automated per-customer portal rules are best-in-class. Your submission process is not the bottleneck."
    ],
    "ps_collections": [
        "Ad-hoc collections means your AR team chases whoever shouts loudest, not whoever represents the most risk. Cash recovery is inefficient.",
        "First-in-first-out is fair but not smart — a $500 invoice at 31 days gets chased before a $50,000 invoice at 29 days.",
        "Prioritising by amount is better, but misses payment behaviour. A customer who always pays at 60 days doesn't need chasing at 31.",
        "Risk-based AI prioritisation is best-in-class. Your collections strategy is not the bottleneck."
    ],
    "ps_aging": [
        "Over 20% of receivables past 90 days is a serious cash risk — write-off probability increases sharply after 90 days.",
        "10-20% past 90 days is concerning. Predictive collections can identify at-risk invoices at 30 days and intervene early.",
        "5-10% past 90 days is within industry norm. Focus on reducing the 60-90 day bucket to prevent migration.",
        "Below 5% past 90 days is excellent — your aging profile is not the bottleneck."
    ],
    "ps_cash_app": [
        "Fully manual cash application is slow and error-prone — unmatched payments sit in suspense accounts, inflating apparent AR.",
        "Partially automated matching handles clean payments but struggles with short-pays, overpays, and missing remittance references.",
        "Mostly automated cash application is strong. AI matching for unstructured remittance advice would close the last 10-15% gap.",
        "Fully automated with AI matching is best-in-class. Your cash application is not the bottleneck."
    ],
}

MODULE_QUESTIONS = {
    "Demand Forecasting": ["df_method", "df_tracking", "df_customer_data"],
    "Order Management": ["om_channel", "om_validation", "om_amendments"],
    "Order Fulfilment & Logistics": ["fl_otif", "fl_wms", "fl_visibility"],
    "Billing & Revenue Mgmt": ["br_invoicing", "br_discount", "br_portal"],
    "Post-Sales & Financial Closure": ["ps_collections", "ps_aging", "ps_cash_app"],
}

MODULE_ICONS = {"Demand Forecasting":"📦","Order Management":"📋","Order Fulfilment & Logistics":"🚚","Billing & Revenue Mgmt":"💰","Post-Sales & Financial Closure":"🏦"}

def render_health_banner(show_modules):
    """Compact health check strip. show_modules = list of module names relevant to this tab. Only shows bottlenecks (Level 1-2 answers)."""
    if not st.session_state.done or not st.session_state.mod_scores:
        return
    ms = st.session_state.mod_scores
    diag = st.session_state.diag_responses
    ds = get_diag_scores(diag)
    data_scores = {"Demand Forecasting":min(100,round(st.session_state.dm["accuracy"]*0.7+max(0,20-abs(st.session_state.dm["bias"]))*1.5)),"Order Management":max(0,min(100,round(100-st.session_state.om["err"]*5-st.session_state.om["disp"]*3-st.session_state.om["amend"]*0.5))),"Order Fulfilment & Logistics":max(0,min(100,round(st.session_state.fl["otif"]*0.8+max(0,10-st.session_state.fl["return_rate"])*2))),"Billing & Revenue Mgmt":max(0,min(100,round(100-st.session_state.bl["err"]*8-st.session_state.bl["disp"]*4))),"Post-Sales & Financial Closure":st.session_state.ps["score"]}

    # Collect only bottleneck items (Level 1-2) for relevant modules
    bottlenecks = []
    for mod_name in show_modules:
        if mod_name not in ms:
            continue
        q_keys = MODULE_QUESTIONS.get(mod_name, [])
        for qk in q_keys:
            ans_idx = diag.get(qk, 0)
            if ans_idx >= 2:  # Level 3-4 = not a bottleneck, skip
                continue
            q_text, ans_text = "", ""
            for mod_d, qs in DIAGNOSTIC.items():
                for q in qs:
                    if q["key"] == qk:
                        q_text, ans_text = q["q"], q["opts"][ans_idx]
                        break
            insight = MATURITY_INSIGHTS.get(qk, ["","","",""])[ans_idx]
            bottlenecks.append({"mod": mod_name, "q": q_text, "ans": ans_text, "insight": insight, "level": ans_idx + 1})

    if not bottlenecks:
        # No bottlenecks — show a compact green strip
        pills = " ".join([f'<span style="display:inline-flex;align-items:center;gap:4px;padding:3px 10px;border-radius:8px;background:#f0fdf4;border:1px solid #bbf7d0;font-size:0.72rem;font-weight:600;color:#166534;margin-right:4px">{MODULE_ICONS.get(m,"")} {ms[m]}</span>' for m in show_modules if m in ms])
        st.markdown(f'<div style="display:flex;align-items:center;gap:10px;padding:8px 14px;background:#f0fdf4;border:1px solid #bbf7d0;border-radius:10px;margin-bottom:1rem"><span style="font-size:0.75rem;color:#166534;font-weight:500">✓ No process bottlenecks on this view</span><div style="margin-left:auto">{pills}</div></div>',unsafe_allow_html=True)
        return

    # Find the single biggest drag
    relevant_gaps = {m: data_scores.get(m,50) - ds.get(m,50) for m in show_modules if m in ms}
    biggest = max(relevant_gaps, key=relevant_gaps.get) if relevant_gaps else show_modules[0]
    drag_pts = relevant_gaps.get(biggest, 0)

    # Module score pills (compact, inline)
    pills_html = ""
    arrow_html = '<span style="font-size:0.6rem;color:#dc2626">▼</span>'
    for m in show_modules:
        if m not in ms: continue
        sc = scolor(ms[m])
        has_issues = any(b["mod"] == m for b in bottlenecks)
        bg = "#fef2f2" if ms[m] < 45 else "#fffbeb" if ms[m] < 70 else "#f0fdf4"
        border = "#fecaca" if ms[m] < 45 else "#fde68a" if ms[m] < 70 else "#bbf7d0"
        trailing = arrow_html if has_issues else ""
        pills_html += f'<span style="display:inline-flex;align-items:center;gap:4px;padding:3px 10px;border-radius:8px;background:{bg};border:1px solid {border};font-size:0.72rem;margin-right:4px"><span style="opacity:0.7">{MODULE_ICONS.get(m,"")}</span><span style="font-family:JetBrains Mono;font-weight:700;color:{sc}">{ms[m]}</span>{trailing}</span>'

    # Headline
    if drag_pts > 10:
        headline = f'<strong>{biggest}</strong> — your processes are costing you {drag_pts} points. {len(bottlenecks)} bottleneck{"s" if len(bottlenecks)!=1 else ""} found below.'
    else:
        headline = f'{len(bottlenecks)} process bottleneck{"s" if len(bottlenecks)!=1 else ""} detected — these are keeping your scores down.'

    # Render the strip
    st.markdown(f'''<div style="background:linear-gradient(135deg,#fefce8,#fff7ed);border:1px solid #fed7aa;border-radius:10px;padding:8px 14px;margin-bottom:0.75rem">
        <div style="display:flex;align-items:center;justify-content:space-between;gap:12px">
            <div style="font-size:0.78rem;color:#92400e">⚠ {headline}</div>
            <div style="display:flex;align-items:center;flex-shrink:0">{pills_html}</div>
        </div>
    </div>''',unsafe_allow_html=True)

    # Bottleneck rows — collapsible
    if len(bottlenecks) > 0:
        with st.expander(f"📋 {len(bottlenecks)} maturity bottleneck{'s' if len(bottlenecks)!=1 else ''} — click to see details", expanded=False):
            for b in bottlenecks:
                lv_color = "#dc2626" if b["level"] == 1 else "#f59e0b"
                lv_bg = "#fef2f2" if b["level"] == 1 else "#fffbeb"
                st.markdown(f'''<div style="display:flex;align-items:flex-start;gap:10px;padding:5px 0;border-bottom:1px solid #f1f5f9">
                    <span style="font-size:0.6rem;font-weight:700;padding:2px 6px;border-radius:6px;background:{lv_bg};color:{lv_color}">L{b["level"]}</span>
                    <div><span style="font-size:0.75rem;font-weight:600;color:#0f172a">{b["ans"]}</span> <span style="font-size:0.68rem;color:#94a3b8">· {b["mod"]}</span><div style="font-size:0.7rem;color:#64748b;margin-top:1px">{b["insight"]}</div></div>
                </div>''',unsafe_allow_html=True)
    st.markdown('<div style="height:4px"></div>',unsafe_allow_html=True)

DEFS={"fc_df":None,"o2c_df":None,"maturity_df":None,"fc_hash":None,"o2c_hash":None,"mat_hash":None,"dm":None,"om":None,"fl":None,"bl":None,"ps":None,"mod_scores":None,"ai_exec":None,"ai_agents":None,"done":False,"news":None,"wb":None,"gt":None,"market_ai":None,"market_fetched":False,"region":"Singapore","industry":"F&B / FMCG","diag_responses":{},"inv_days":45,"dpo_days":30,"display_ccy":"USD","ltv":None,"cash_app":None,"disputes":None,"order_ingest":None,"invoice_demo":None,"yearly_metrics":None}
for k,v in DEFS.items():
    if k not in st.session_state: st.session_state[k]=v
def reset():
    for k,v in DEFS.items(): st.session_state[k]=v

ccy=st.session_state.display_ccy; ccy_label=CURRENCIES.get(ccy,CURRENCIES["USD"])["label"]
st.markdown(f'<div class="tct-header"><div><div class="tct-title">Revenue Optimizer</div><div class="tct-subtitle">AI-Powered Revenue Operations Intelligence Platform</div></div><div style="display:flex;align-items:center;gap:12px"><span class="tct-badge">AI Engine: Active</span><span class="tct-currency">{ccy_label}</span></div></div>',unsafe_allow_html=True)
h1,h2,h3,h4=st.columns([1,1,0.7,0.5])
with h1: region=st.selectbox("Region",list(REGIONS.keys()),index=list(REGIONS.keys()).index(st.session_state.region)); st.session_state.region=region
with h2: industry=st.selectbox("Industry",list(INDUSTRIES.keys()),index=list(INDUSTRIES.keys()).index(st.session_state.industry)); st.session_state.industry=industry
with h3:
    lc=REGIONS[region]["currency"]; co=["USD",lc] if lc!="USD" else ["USD"]; ci=co.index(st.session_state.display_ccy) if st.session_state.display_ccy in co else 0
    sel=st.selectbox("Currency",co,index=ci,format_func=lambda x:CURRENCIES[x]["label"]); st.session_state.display_ccy=sel; ccy=sel
with h4:
    st.markdown("<br>",unsafe_allow_html=True)
    if st.button("🔄 Refresh"): reset(); st.rerun()

tabs=st.tabs(["⚙ Setup","🏥 Executive Health Report","📊 ForecastIQ Dashboard","📋 O2C Performance Hub","💰 CFO Dashboard","🏦 Cash App & LTV Engine"])

with tabs[0]:
    st.markdown('<div style="font-size:1.3rem;font-weight:700;color:#0c1222;letter-spacing:-0.02em">Setup & Configuration</div><div style="font-size:0.88rem;color:#64748b;margin-bottom:1.5rem">Upload three data files and click Run. No manual configuration needed.</div>',unsafe_allow_html=True)
    st.markdown('<div class="section-card"><div class="section-title">Data Templates — Download & Fill</div><div class="mex" style="margin-top:-0.5rem;margin-bottom:0.75rem">Download templates, fill with your data, re-upload. Or click Load Demo Data for pre-built sample data (Jan 2023 – May 2026).</div>',unsafe_allow_html=True)
    tpl1,tpl2,tpl3=st.columns(3)
    with tpl1:
        tpl_fc = sample_demand()
        st.download_button("⬇ Demand & Forecast", tpl_fc.to_csv(index=False).encode("utf-8"), "demand_forecast_template.csv", "text/csv", key="dl_fc", use_container_width=True)
        st.markdown(f'<div style="font-size:0.72rem;color:#94a3b8;margin-top:0.2rem">{len(tpl_fc)} rows · 4 SKUs × 36 months</div>',unsafe_allow_html=True)
    with tpl2:
        tpl_o2c = sample_o2c("Singapore")
        st.download_button("⬇ Order-to-Cash", tpl_o2c.to_csv(index=False).encode("utf-8"), "order_to_cash_template.csv", "text/csv", key="dl_o2c", use_container_width=True)
        st.markdown(f'<div style="font-size:0.72rem;color:#94a3b8;margin-top:0.2rem">{len(tpl_o2c)} rows · ~20 orders/month × 36 months</div>',unsafe_allow_html=True)
    with tpl3:
        tpl_mat = sample_maturity()
        st.download_button("⬇ Maturity Assessment", tpl_mat.to_csv(index=False).encode("utf-8"), "maturity_assessment_template.csv", "text/csv", key="dl_mat", use_container_width=True)
        st.markdown('<div style="font-size:0.72rem;color:#94a3b8;margin-top:0.2rem">18 rows · region, industry, currency + 15 maturity levels</div>',unsafe_allow_html=True)
    st.markdown("</div>",unsafe_allow_html=True)
    st.markdown('<div class="section-card"><div class="section-title">Upload Your Data</div>',unsafe_allow_html=True)
    u1,u2,u3=st.columns(3)
    with u1:
        uf1=st.file_uploader("Demand & Forecast CSV",type=["csv"],key="fu_fc")
        if uf1:
            h=hash(uf1.read()); uf1.seek(0)
            if h!=st.session_state.fc_hash:
                st.session_state.fc_df=pd.read_csv(uf1); st.session_state.fc_hash=h; st.session_state.done=False
            st.success(f"✓ {len(st.session_state.fc_df)} rows loaded")
    with u2:
        uf2=st.file_uploader("Order-to-Cash CSV",type=["csv"],key="fu_o2c")
        if uf2:
            h=hash(uf2.read()); uf2.seek(0)
            if h!=st.session_state.o2c_hash:
                st.session_state.o2c_df=pd.read_csv(uf2); st.session_state.o2c_hash=h; st.session_state.done=False
                if "Inventory_Days" in st.session_state.o2c_df.columns: st.session_state.inv_days=int(st.session_state.o2c_df["Inventory_Days"].iloc[0])
                if "DPO_Days" in st.session_state.o2c_df.columns: st.session_state.dpo_days=int(st.session_state.o2c_df["DPO_Days"].iloc[0])
            st.success(f"✓ {len(st.session_state.o2c_df)} rows loaded")
    with u3:
        uf3=st.file_uploader("Maturity Assessment CSV",type=["csv"],key="fu_mat")
        if uf3:
            h=hash(uf3.read()); uf3.seek(0)
            if h!=st.session_state.mat_hash:
                st.session_state.maturity_df=pd.read_csv(uf3); st.session_state.mat_hash=h; st.session_state.done=False
                r,ind,cur,diag=parse_maturity_csv(st.session_state.maturity_df)
                st.session_state.region=r; st.session_state.industry=ind; st.session_state.display_ccy=cur; st.session_state.diag_responses=diag
            st.success(f"✓ Config: {st.session_state.region}, {st.session_state.industry}")
    st.markdown("</div>",unsafe_allow_html=True)
    b1,b2=st.columns([1,1])
    with b1:
        if st.button("📥 Load Demo Data",use_container_width=True):
            st.session_state.fc_df=sample_demand(); st.session_state.o2c_df=sample_o2c("Singapore"); st.session_state.maturity_df=sample_maturity()
            r,ind,cur,diag=parse_maturity_csv(st.session_state.maturity_df)
            st.session_state.region=r; st.session_state.industry=ind; st.session_state.display_ccy=cur; st.session_state.diag_responses=diag
            if "Inventory_Days" in st.session_state.o2c_df.columns: st.session_state.inv_days=int(st.session_state.o2c_df["Inventory_Days"].iloc[0])
            if "DPO_Days" in st.session_state.o2c_df.columns: st.session_state.dpo_days=int(st.session_state.o2c_df["DPO_Days"].iloc[0])
            st.session_state.fc_hash="s"; st.session_state.o2c_hash="s"; st.session_state.mat_hash="s"; st.session_state.done=False; st.rerun()
    with b2:
        if st.button("🚀 Run Analysis",use_container_width=True):
            if st.session_state.fc_df is None or st.session_state.o2c_df is None:
                st.error("Load data first — click Load Demo Data or upload CSVs above.")
            else:
                region=st.session_state.region; industry=st.session_state.industry; ccy=st.session_state.display_ccy
                inv_d=st.session_state.inv_days; dpo_d=st.session_state.dpo_days; ds=get_diag_scores(st.session_state.diag_responses)
                with st.spinner("Computing..."): st.session_state.dm=calc_demand(st.session_state.fc_df); st.session_state.om=calc_order_mgmt(st.session_state.o2c_df); st.session_state.fl=calc_fulfilment(st.session_state.o2c_df,industry); st.session_state.bl=calc_billing(st.session_state.o2c_df,industry); st.session_state.ps=calc_post_sales(st.session_state.o2c_df,industry,inv_d,dpo_d); st.session_state.mod_scores=calc_module_scores(st.session_state.dm,st.session_state.om,st.session_state.fl,st.session_state.bl,st.session_state.ps,ds)
                with st.spinner("LTV & Cash App..."): st.session_state.ltv=calc_customer_ltv(st.session_state.o2c_df,industry); st.session_state.cash_app=calc_cash_app_simulation(st.session_state.o2c_df); st.session_state.disputes=calc_dispute_workflow(st.session_state.o2c_df); st.session_state.order_ingest=generate_order_ingest_demo(region); st.session_state.invoice_demo=generate_invoice_demo(st.session_state.o2c_df,region)
                yearly={}
                for yr in get_demand_years(st.session_state.fc_df)[1:]:
                    fd=filter_demand_by_year(st.session_state.fc_df,yr); od=filter_by_year(st.session_state.o2c_df,yr)
                    if len(fd)>0 and len(od)>0:
                        yd=calc_demand(fd); yo=calc_order_mgmt(od); yf=calc_fulfilment(od,industry); yb=calc_billing(od,industry); yp=calc_post_sales(od,industry,inv_d,dpo_d)
                        yearly[yr]={"accuracy":yd["accuracy"],"mape":yd["mape"],"bias":yd["bias"],"otif":yd["otif"],"dso":yb["dso"],"err":yo["err"],"disp":yo["disp"],"leakage_pct":round((yb["leak_total"]/max(yb["rev"],1))*100,1),"ccc":yp["ccc"],"score":yp["score"],"rev":yb["rev"]}
                st.session_state.yearly_metrics=yearly
                with st.spinner("AI insights..."):
                    try: st.session_state.ai_exec=get_executive_ai(st.session_state.dm,st.session_state.om,st.session_state.fl,st.session_state.bl,st.session_state.ps,st.session_state.mod_scores,ds,region,industry,ccy)
                    except: pass
                with st.spinner("Agent simulation..."):
                    try: st.session_state.ai_agents=get_agent_simulation(st.session_state.dm,st.session_state.om,st.session_state.fl,st.session_state.bl,st.session_state.ps,st.session_state.mod_scores,region,industry,ccy)
                    except: pass
                st.session_state.done=True; st.rerun()
    if st.session_state.fc_df is not None:
        st.markdown(f'<div class="info-box">📊 Data loaded — Demand: {len(st.session_state.fc_df)} rows · O2C: {len(st.session_state.o2c_df) if st.session_state.o2c_df is not None else 0} rows · Config: {st.session_state.region}, {st.session_state.industry}, {st.session_state.display_ccy}</div>',unsafe_allow_html=True)
    if st.session_state.done: st.success("Analysis complete — explore tabs above.")


# ==================== TAB 1: EXECUTIVE HEALTH REPORT ====================
with tabs[1]:
    if not st.session_state.done: st.info("Complete Setup and click Run Full Analysis to generate your health report.")
    else:
        ms = st.session_state.mod_scores; diag = st.session_state.diag_responses; ds = get_diag_scores(diag)
        data_scores = {"Demand Forecasting":min(100,round(st.session_state.dm["accuracy"]*0.7+max(0,20-abs(st.session_state.dm["bias"]))*1.5)),"Order Management":max(0,min(100,round(100-st.session_state.om["err"]*5-st.session_state.om["disp"]*3-st.session_state.om["amend"]*0.5))),"Order Fulfilment & Logistics":max(0,min(100,round(st.session_state.fl["otif"]*0.8+max(0,10-st.session_state.fl["return_rate"])*2))),"Billing & Revenue Mgmt":max(0,min(100,round(100-st.session_state.bl["err"]*8-st.session_state.bl["disp"]*4))),"Post-Sales & Financial Closure":st.session_state.ps["score"]}
        overall = round(sum(ms.values()) / max(len(ms), 1))
        overall_label = "Good" if overall >= 70 else "At Risk" if overall >= 45 else "Critical"
        overall_color = scolor(overall)

        # Compute drag per module
        drags = {}
        for m in ms:
            drags[m] = {"data": data_scores.get(m, 50), "maturity": ds.get(m, 50), "blended": ms[m], "drag": data_scores.get(m, 50) - ms[m]}
        total_drag = sum(d["drag"] for d in drags.values() if d["drag"] > 0)
        worst_module = max(drags, key=lambda m: drags[m]["drag"]) if drags else ""

        # One-sentence diagnosis
        if total_drag > 30:
            diagnosis = f"Your data quality is solid across most modules, but manual processes — particularly in {worst_module} — are suppressing your overall O2C performance by an estimated {total_drag} points. Addressing the bottlenecks below would unlock significant operational and financial improvement."
        elif total_drag > 10:
            diagnosis = f"Your operations are functional but process gaps in {worst_module} and adjacent modules are leaving value on the table. Targeted investment in the recommendations below would close the gap."
        else:
            diagnosis = "Your data and processes are well-aligned. Focus on the refinement recommendations below to move from good to best-in-class."

        # === DUAL HEALTH SCORES: DEMAND + O2C ===
        df_score = ms.get("Demand Forecasting", 50)
        o2c_mods = ["Order Management","Order Fulfilment & Logistics","Billing & Revenue Mgmt","Post-Sales & Financial Closure"]
        o2c_score = round(sum(ms.get(m,50) for m in o2c_mods) / len(o2c_mods))
        df_label = "Good" if df_score >= 70 else "At Risk" if df_score >= 45 else "Critical"
        o2c_label = "Good" if o2c_score >= 70 else "At Risk" if o2c_score >= 45 else "Critical"
        df_color = scolor(df_score); o2c_color = scolor(o2c_score)

        st.markdown(f'''<div style="background:linear-gradient(135deg,#0c1222 0%,#162040 50%,#1a2a52 100%);border-radius:16px;padding:1.75rem 2rem;margin-bottom:1.25rem;box-shadow:0 4px 24px rgba(10,22,40,0.15)">
            <div style="font-size:1rem;font-weight:600;color:white;margin-bottom:0.5rem">Executive Health Report</div>
            <div style="font-size:0.82rem;color:rgba(203,213,225,0.9);line-height:1.55;margin-bottom:1.25rem">{diagnosis}</div>
            <div style="display:flex;align-items:center;gap:2rem;flex-wrap:wrap">
                <div style="text-align:center">
                    <div style="font-size:0.6rem;font-weight:600;letter-spacing:0.1em;text-transform:uppercase;color:rgba(148,163,184,0.7);margin-bottom:0.3rem">📦 DEMAND FORECASTING</div>
                    <div style="position:relative;width:100px;height:100px;margin:0 auto">
                        <svg viewBox="0 0 100 100" style="transform:rotate(-90deg)"><circle cx="50" cy="50" r="42" fill="none" stroke="rgba(255,255,255,0.08)" stroke-width="8"/><circle cx="50" cy="50" r="42" fill="none" stroke="{df_color}" stroke-width="8" stroke-dasharray="{df_score*2.64} 264" stroke-linecap="round"/></svg>
                        <div style="position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);text-align:center"><div style="font-family:JetBrains Mono;font-size:1.6rem;font-weight:700;color:white">{df_score}</div><div style="font-size:0.62rem;font-weight:600;color:{df_color}">{df_label}</div></div>
                    </div>
                </div>
                <div style="text-align:center">
                    <div style="font-size:0.6rem;font-weight:600;letter-spacing:0.1em;text-transform:uppercase;color:rgba(148,163,184,0.7);margin-bottom:0.3rem">💰 ORDER-TO-CASH</div>
                    <div style="position:relative;width:100px;height:100px;margin:0 auto">
                        <svg viewBox="0 0 100 100" style="transform:rotate(-90deg)"><circle cx="50" cy="50" r="42" fill="none" stroke="rgba(255,255,255,0.08)" stroke-width="8"/><circle cx="50" cy="50" r="42" fill="none" stroke="{o2c_color}" stroke-width="8" stroke-dasharray="{o2c_score*2.64} 264" stroke-linecap="round"/></svg>
                        <div style="position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);text-align:center"><div style="font-family:JetBrains Mono;font-size:1.6rem;font-weight:700;color:white">{o2c_score}</div><div style="font-size:0.62rem;font-weight:600;color:{o2c_color}">{o2c_label}</div></div>
                    </div>
                </div>
                <div style="text-align:center">
                    <div style="font-size:0.6rem;font-weight:600;letter-spacing:0.1em;text-transform:uppercase;color:rgba(148,163,184,0.7);margin-bottom:0.3rem">⚡ OVERALL</div>
                    <div style="position:relative;width:100px;height:100px;margin:0 auto">
                        <svg viewBox="0 0 100 100" style="transform:rotate(-90deg)"><circle cx="50" cy="50" r="42" fill="none" stroke="rgba(255,255,255,0.08)" stroke-width="8"/><circle cx="50" cy="50" r="42" fill="none" stroke="{overall_color}" stroke-width="8" stroke-dasharray="{overall*2.64} 264" stroke-linecap="round"/></svg>
                        <div style="position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);text-align:center"><div style="font-family:JetBrains Mono;font-size:1.6rem;font-weight:700;color:white">{overall}</div><div style="font-size:0.62rem;font-weight:600;color:{overall_color}">{overall_label}</div></div>
                    </div>
                </div>
                <div style="flex:1;display:flex;flex-wrap:wrap;gap:10px;justify-content:flex-end">
                    <div style="background:rgba(255,255,255,0.06);border:1px solid rgba(255,255,255,0.1);border-radius:10px;padding:8px 14px;text-align:center">
                        <div style="font-size:0.58rem;color:rgba(148,163,184,0.7);text-transform:uppercase;letter-spacing:0.08em">Process Drag</div>
                        <div style="font-family:JetBrains Mono;font-size:1rem;font-weight:700;color:{"#f87171" if total_drag>20 else "#fbbf24" if total_drag>5 else "#4ade80"}">{total_drag} pts</div>
                    </div>
                    <div style="background:rgba(255,255,255,0.06);border:1px solid rgba(255,255,255,0.1);border-radius:10px;padding:8px 14px;text-align:center">
                        <div style="font-size:0.58rem;color:rgba(148,163,184,0.7);text-transform:uppercase;letter-spacing:0.08em">Revenue at Risk</div>
                        <div style="font-family:JetBrains Mono;font-size:1rem;font-weight:700;color:#fbbf24">{fmtc(st.session_state.bl["leak_total"],ccy,True)}</div>
                    </div>
                    <div style="background:rgba(255,255,255,0.06);border:1px solid rgba(255,255,255,0.1);border-radius:10px;padding:8px 14px;text-align:center">
                        <div style="font-size:0.58rem;color:rgba(148,163,184,0.7);text-transform:uppercase;letter-spacing:0.08em">DSO Gap</div>
                        <div style="font-family:JetBrains Mono;font-size:1rem;font-weight:700;color:{"#f87171" if st.session_state.bl["gap"]>5 else "#4ade80"}">{st.session_state.bl["gap"]:+.0f}d</div>
                    </div>
                </div>
            </div>
        </div>''',unsafe_allow_html=True)

        # === MODULE HEALTH BARS ===
        st.markdown('<div class="section-card"><div class="section-title">Module Health — Data vs Process Maturity</div><div class="mex" style="margin-top:-0.5rem;margin-bottom:1rem">Each bar shows your blended score. The hatched zone shows where process maturity is holding back your data potential. Right label shows overall status and any drag.</div>',unsafe_allow_html=True)
        for mod_name in ms:
            d = drags[mod_name]
            sc = scolor(d["blended"])
            icon = MODULE_ICONS.get(mod_name, "")
            drag_val = d["drag"]
            # Status label: combine health + drag
            if d["blended"] < 30:
                status_label = f'Critical ({d["blended"]}/100)'
                status_co = "#dc2626"
                if drag_val > 5: status_label += f' · −{drag_val} pts drag'
            elif d["blended"] < 50:
                status_label = f'Needs work ({d["blended"]}/100)'
                status_co = "#ea580c"
                if drag_val > 5: status_label += f' · −{drag_val} pts drag'
            elif d["blended"] < 70:
                status_label = f'Improving ({d["blended"]}/100)'
                status_co = "#f59e0b"
                if drag_val > 5: status_label += f' · −{drag_val} pts drag'
            else:
                status_label = f'Good ({d["blended"]}/100)'
                status_co = "#16a34a"
                if drag_val > 5: status_label += f' · −{drag_val} pts drag'
            # Bar background color based on severity
            bar_bg = "#fef2f2" if d["blended"] < 30 else "#fffbeb" if d["blended"] < 50 else "#f1f5f9"
            st.markdown(f'''<div style="display:flex;align-items:center;gap:14px;padding:10px 8px;border-bottom:1px solid #f1f5f9;background:{bar_bg};border-radius:8px;margin-bottom:4px">
                <div style="width:200px;flex-shrink:0;font-size:0.82rem;font-weight:600;color:#0f172a">{icon} {mod_name}</div>
                <div style="flex:1;position:relative;height:24px;background:#e2e8f0;border-radius:6px;overflow:hidden">
                    <div style="position:absolute;left:0;top:0;height:100%;width:{d["data"]}%;background:rgba(3,105,161,0.15);border-radius:6px"></div>
                    <div style="position:absolute;left:0;top:0;height:100%;width:{d["blended"]}%;background:{sc};border-radius:6px"></div>
                    <div style="position:absolute;left:{d["blended"]}%;top:0;height:100%;width:{max(0,d["data"]-d["blended"])}%;background:repeating-linear-gradient(45deg,transparent,transparent 3px,rgba(220,38,38,0.15) 3px,rgba(220,38,38,0.15) 6px);border-radius:0 6px 6px 0"></div>
                    <div style="position:absolute;top:50%;left:8px;transform:translateY(-50%);font-family:JetBrains Mono;font-size:0.75rem;font-weight:700;color:white;text-shadow:0 1px 3px rgba(0,0,0,0.4)">{d["blended"]}</div>
                </div>
                <div style="width:180px;flex-shrink:0;text-align:right;font-family:JetBrains Mono;font-size:0.72rem;font-weight:700;color:{status_co}">{status_label}</div>
            </div>''',unsafe_allow_html=True)
        st.markdown('<div style="display:flex;gap:16px;margin-top:0.75rem;font-size:0.68rem;color:#94a3b8"><span>█ Blended score (what you achieve today)</span><span style="color:#0369a1">░ Data potential (if processes were optimised)</span><span style="color:#dc2626">▒ Process drag (your setup answers)</span></div>',unsafe_allow_html=True)
        st.markdown("</div>",unsafe_allow_html=True)

        # === 3-YEAR TREND ===
        ym = st.session_state.yearly_metrics
        if ym and len(ym) > 1:
            yrs = sorted(ym.keys()); first=ym[yrs[0]]; last=ym[yrs[-1]]
            acc_d=last["accuracy"]-first["accuracy"]; dso_d=last["dso"]-first["dso"]; otif_d=last["otif"]-first["otif"]; err_d=last["err"]-first["err"]
            # Trend metric cards
            st.markdown('<div class="section-card"><div class="section-title">3-Year Performance Trend</div>',unsafe_allow_html=True)
            tr1,tr2,tr3,tr4=st.columns(4)
            with tr1: st.markdown(f'<div style="text-align:center"><div style="font-size:0.65rem;font-weight:600;color:#64748b;text-transform:uppercase;letter-spacing:0.08em">Forecast Accuracy</div><div style="font-family:JetBrains Mono;font-size:1.3rem;font-weight:700;color:{"#16a34a" if acc_d>0 else "#dc2626"}">{acc_d:+.1f}%</div><div style="font-size:0.72rem;color:#94a3b8">{first["accuracy"]:.0f}% → {last["accuracy"]:.0f}%</div></div>',unsafe_allow_html=True)
            with tr2: st.markdown(f'<div style="text-align:center"><div style="font-size:0.65rem;font-weight:600;color:#64748b;text-transform:uppercase;letter-spacing:0.08em">DSO</div><div style="font-family:JetBrains Mono;font-size:1.3rem;font-weight:700;color:{"#16a34a" if dso_d<0 else "#dc2626"}">{dso_d:+.1f}d</div><div style="font-size:0.72rem;color:#94a3b8">{first["dso"]:.0f}d → {last["dso"]:.0f}d</div></div>',unsafe_allow_html=True)
            with tr3: st.markdown(f'<div style="text-align:center"><div style="font-size:0.65rem;font-weight:600;color:#64748b;text-transform:uppercase;letter-spacing:0.08em">OTIF</div><div style="font-family:JetBrains Mono;font-size:1.3rem;font-weight:700;color:{"#16a34a" if otif_d>0 else "#dc2626"}">{otif_d:+.1f}%</div><div style="font-size:0.72rem;color:#94a3b8">{first["otif"]:.0f}% → {last["otif"]:.0f}%</div></div>',unsafe_allow_html=True)
            with tr4: st.markdown(f'<div style="text-align:center"><div style="font-size:0.65rem;font-weight:600;color:#64748b;text-transform:uppercase;letter-spacing:0.08em">Error Rate</div><div style="font-family:JetBrains Mono;font-size:1.3rem;font-weight:700;color:{"#16a34a" if err_d<0 else "#dc2626"}">{err_d:+.1f}%</div><div style="font-size:0.72rem;color:#94a3b8">{first["err"]:.0f}% → {last["err"]:.0f}%</div></div>',unsafe_allow_html=True)
            # Natural language trend analysis
            trend_parts = []
            if acc_d > 5: trend_parts.append(f"Forecast accuracy improved significantly by {acc_d:.0f} percentage points — your demand planning matured over this period")
            elif acc_d > 0: trend_parts.append(f"Forecast accuracy improved modestly ({acc_d:+.1f}%) — progress is real but slow")
            else: trend_parts.append(f"Forecast accuracy declined ({acc_d:+.1f}%) — this warrants investigation into demand signal quality or model drift")
            if dso_d < -5: trend_parts.append(f"DSO dropped {abs(dso_d):.0f} days — your collections and invoicing processes got faster")
            elif dso_d < 0: trend_parts.append(f"DSO improved slightly ({dso_d:+.0f}d)")
            else: trend_parts.append(f"DSO increased by {dso_d:.0f} days — cash cycle is getting longer, not shorter")
            if last["leakage_pct"] > 3: trend_parts.append(f"Revenue leakage at {last['leakage_pct']}% in the latest year is still above the 3% threshold — pricing governance remains a gap")
            st.markdown(f'<div style="background:#f8fafc;border-radius:10px;padding:10px 14px;font-size:0.78rem;color:#334155;line-height:1.55;margin-top:0.75rem">{". ".join(trend_parts)}.</div>',unsafe_allow_html=True)
            st.markdown("</div>",unsafe_allow_html=True)

        # === AI INSIGHT PANELS ===
        ai_l,ai_r=st.columns(2)
        with ai_l:
            dm=st.session_state.dm
            fc_insight = f'Forecast accuracy at {dm["accuracy"]}% with {dm["mape"]:.1f}% MAPE and {dm["bias"]:+.1f}% bias.'
            if dm["accuracy"] < 85: fc_insight += f' Below 85% target — {"systematic under-forecasting" if dm["bias"]<-3 else "systematic over-forecasting" if dm["bias"]>3 else "high variance across SKUs"} is the primary driver.'
            if ym and len(ym)>1:
                yrs=sorted(ym.keys()); fc_insight += f' Accuracy moved {ym[yrs[-1]]["accuracy"]-ym[yrs[0]]["accuracy"]:+.1f}% over {len(ym)} years.'
            st.markdown(f'<div style="background:#f0fdf4;border:1px solid #bbf7d0;border-radius:10px;padding:10px 14px;font-size:0.78rem;color:#166534"><strong>📦 Demand Intelligence:</strong> {fc_insight}</div>',unsafe_allow_html=True)
        with ai_r:
            bl=st.session_state.bl; ps=st.session_state.ps
            o2c_insight = f'DSO {bl["dso"]:.0f}d ({"on target" if bl["gap"]<=0 else f"{bl["gap"]:.0f}d above benchmark"}). Revenue leakage {fmtc(bl["leak_total"],ccy,True)} ({round(bl["leak_total"]/max(bl["rev"],1)*100,1)}%).'
            if ps["aging"]["90d"] > 10: o2c_insight += f' Warning: {ps["aging"]["90d"]}% AR past 90 days.'
            if ym and len(ym)>1:
                yrs=sorted(ym.keys()); o2c_insight += f' DSO trend: {ym[yrs[-1]]["dso"]-ym[yrs[0]]["dso"]:+.1f}d over {len(ym)} years.'
            st.markdown(f'<div style="background:#eff6ff;border:1px solid #bfdbfe;border-radius:10px;padding:10px 14px;font-size:0.78rem;color:#1e40af"><strong>💰 O2C Intelligence:</strong> {o2c_insight}</div>',unsafe_allow_html=True)

        # === RECOMMENDATIONS (concise) ===
        # Build recommendations from bottleneck questions and data gaps
        all_recs = []
        # Recommendation templates: (question_key, answer_index, recommendation, module, timeline, impact_func)
        REC_MAP = {
            ("df_method", 0): {"action": "Replace spreadsheet forecasting with ML-assisted demand planning", "module": "Demand Forecasting", "timeline": "8-12 weeks", "impact": "Forecast accuracy improvement of 15-25%, reducing excess inventory and stockouts", "tier": 1},
            ("df_method", 1): {"action": "Upgrade from basic ERP forecasting to AI ensemble models with external signals", "module": "Demand Forecasting", "timeline": "10-14 weeks", "impact": "10-15% accuracy improvement by incorporating promotions, seasonality, and market data", "tier": 1},
            ("df_tracking", 0): {"action": "Implement forecast accuracy tracking (MAPE, bias) with monthly review cadence", "module": "Demand Forecasting", "timeline": "2-4 weeks", "impact": "Visibility into forecast performance — you can't improve what you can't measure", "tier": 1},
            ("df_tracking", 1): {"action": "Move from occasional to structured monthly forecast accuracy reviews", "module": "Demand Forecasting", "timeline": "2-3 weeks", "impact": "Catch systematic bias before it compounds into inventory and service failures", "tier": 2},
            ("df_customer_data", 0): {"action": "Deploy DistributorConnect portal to capture customer demand signals", "module": "Demand Forecasting", "timeline": "12-16 weeks", "impact": "Reduce bullwhip effect by replacing guesswork with actual customer data", "tier": 2},
            ("df_customer_data", 1): {"action": "Expand customer forecast data coverage beyond 50% using lightweight portals", "module": "Demand Forecasting", "timeline": "8-12 weeks", "impact": "Close demand signal blind spots for mid-tier customers", "tier": 2},
            ("om_channel", 0): {"action": "Deploy OrderIngest Hub for unified multi-channel order capture with LLM/OCR", "module": "Order Management", "timeline": "6-10 weeks", "impact": "Eliminate manual re-keying errors — the #1 source of downstream disputes", "tier": 1},
            ("om_channel", 1): {"action": "Add AI-powered order parsing for non-EDI channels (email, WhatsApp, fax)", "module": "Order Management", "timeline": "6-8 weeks", "impact": "Reduce order entry errors from format inconsistency across channels", "tier": 1},
            ("om_validation", 0): {"action": "Automate order validation with ATP, credit check, and price verification", "module": "Order Management", "timeline": "6-8 weeks", "impact": "Stop errors at entry — prevents cascade into fulfilment, billing, and disputes", "tier": 1},
            ("om_validation", 1): {"action": "Extend partial validation to cover full ATP + BOM + credit + PriceGuard checks", "module": "Order Management", "timeline": "4-6 weeks", "impact": "Close the exceptions gap that causes outsized downstream damage", "tier": 2},
            ("om_amendments", 0): {"action": "Implement order confirmation workflows with amendment cut-off rules", "module": "Order Management", "timeline": "4-6 weeks", "impact": "Reduce 30%+ amendment rate — each amendment costs processing time and error risk", "tier": 1},
            ("om_amendments", 1): {"action": "Tighten amendment windows with ChangeControl Hub audit trail", "module": "Order Management", "timeline": "3-5 weeks", "impact": "Reduce amendments from 15-30% toward <10% with cut-off enforcement", "tier": 2},
            ("fl_otif", 0): {"action": "Implement OTIF tracking with ShipmentTracker and ePOD confirmation", "module": "Fulfilment & Logistics", "timeline": "4-6 weeks", "impact": "Establish baseline fulfilment visibility — currently flying blind on delivery performance", "tier": 1},
            ("fl_otif", 1): {"action": "Formalise OTIF measurement by customer, SKU, and route for root cause analysis", "module": "Fulfilment & Logistics", "timeline": "3-5 weeks", "impact": "Move from estimates to actionable data — identify which routes and customers fail most", "tier": 2},
            ("fl_wms", 0): {"action": "Deploy WMS Optimiser to replace paper-based warehouse management", "module": "Fulfilment & Logistics", "timeline": "10-14 weeks", "impact": "Reduce mispicks, improve dispatch speed, enable FEFO compliance", "tier": 2},
            ("fl_wms", 1): {"action": "Upgrade to advanced WMS with wave planning and route-optimised picking", "module": "Fulfilment & Logistics", "timeline": "8-12 weeks", "impact": "15-20% throughput improvement with optimised pick paths", "tier": 2},
            ("fl_visibility", 0): {"action": "Integrate carrier tracking into LogisticsConnect for real-time shipment visibility", "module": "Fulfilment & Logistics", "timeline": "6-8 weeks", "impact": "Proactive exception management — know about delays before customers do", "tier": 1},
            ("fl_visibility", 1): {"action": "Consolidate carrier tracking into single dashboard with exception alerts", "module": "Fulfilment & Logistics", "timeline": "4-6 weeks", "impact": "Replace reactive carrier-website checks with unified proactive view", "tier": 2},
            ("br_invoicing", 0): {"action": "Deploy BillingEngine auto-invoice trigger on ePOD confirmation", "module": "Billing & Revenue", "timeline": "4-6 weeks", "impact": "Eliminate 24-48 hour billing delay — directly reduces DSO", "tier": 1},
            ("br_invoicing", 1): {"action": "Add auto-trigger on shipment confirmation to remove manual finance step", "module": "Billing & Revenue", "timeline": "3-5 weeks", "impact": "Cut invoice generation time from hours to minutes", "tier": 1},
            ("br_discount", 0): {"action": "Implement PriceGuard Engine for pricing discipline from quote to invoice", "module": "Billing & Revenue", "timeline": "6-8 weeks", "impact": "Close systematic revenue leakage from ad-hoc discounting — typically 1-3% of revenue", "tier": 1},
            ("br_discount", 1): {"action": "Upgrade to rules-based discount governance with real-time enforcement", "module": "Billing & Revenue", "timeline": "4-6 weeks", "impact": "Prevent retroactive approval loopholes that bypass controls", "tier": 2},
            ("br_portal", 0): {"action": "Build automated customer portal submission capability", "module": "Billing & Revenue", "timeline": "8-10 weeks", "impact": "Reduce DSO for portal-dependent customers where manual submission causes delays", "tier": 2},
            ("br_portal", 1): {"action": "Automate per-customer portal rules to eliminate manual upload burden", "module": "Billing & Revenue", "timeline": "6-8 weeks", "impact": "Scale portal compliance without proportional headcount", "tier": 2},
            ("ps_collections", 0): {"action": "Deploy CollectIQ risk-based collections prioritisation", "module": "Post-Sales & Closure", "timeline": "4-6 weeks", "impact": "Chase highest-risk invoices first — not just whoever shouts loudest", "tier": 1},
            ("ps_collections", 1): {"action": "Upgrade from FIFO to intelligent risk-weighted collections queue", "module": "Post-Sales & Closure", "timeline": "3-5 weeks", "impact": "Stop chasing $500 invoices at 31 days while $50K invoices approach risk", "tier": 2},
            ("ps_aging", 0): {"action": "Implement predictive aging alerts at 30 days to prevent 90+ day migration", "module": "Post-Sales & Closure", "timeline": "4-6 weeks", "impact": "20%+ past 90 days is serious write-off risk — early intervention changes trajectory", "tier": 1},
            ("ps_aging", 1): {"action": "Deploy predictive collections to catch at-risk invoices at 30 days", "module": "Post-Sales & Closure", "timeline": "4-6 weeks", "impact": "Reduce 90+ day bucket from 10-20% toward <5%", "tier": 2},
            ("ps_cash_app", 0): {"action": "Deploy CollectIQ auto cash application with AI matching", "module": "Post-Sales & Closure", "timeline": "6-8 weeks", "impact": "Eliminate manual payment matching — reduce suspense account balances and apparent AR", "tier": 1},
            ("ps_cash_app", 1): {"action": "Extend automated matching to handle short-pays and unstructured remittance", "module": "Post-Sales & Closure", "timeline": "4-6 weeks", "impact": "Close the last 20-30% of payments that require manual allocation", "tier": 2},
        }

        for qk, ans_idx in diag.items():
            if ans_idx >= 2: continue
            key = (qk, ans_idx)
            if key in REC_MAP:
                rec = REC_MAP[key].copy()
                for mod_d, qs in DIAGNOSTIC.items():
                    for q in qs:
                        if q["key"] == qk:
                            rec["because"] = q["opts"][ans_idx]
                            break
                all_recs.append(rec)

        # Data-driven recs (always check)
        if st.session_state.dm["accuracy"] < 85:
            all_recs.append({"action": f"Improve forecast accuracy from {st.session_state.dm['accuracy']}% toward 85%+ target", "module": "Demand Forecasting", "timeline": "Ongoing", "tier": 2, "because": f"Data: accuracy at {st.session_state.dm['accuracy']}%"})
        if st.session_state.bl["gap"] > 5:
            all_recs.append({"action": f"Reduce DSO from {st.session_state.bl['dso']:.0f}d toward {st.session_state.bl['bench']}d benchmark", "module": "Billing & Revenue", "timeline": "4-8 weeks", "tier": 1, "because": f"Data: DSO {st.session_state.bl['gap']:.0f}d above benchmark"})
        if st.session_state.ps["aging"]["90d"] > 5:
            all_recs.append({"action": "Reduce AR aging past 90 days — deploy predictive collections", "module": "Post-Sales & Closure", "timeline": "4-6 weeks", "tier": 1, "because": f"Data: {st.session_state.ps['aging']['90d']}% past 90 days"})
        if st.session_state.om["err"] > 3:
            all_recs.append({"action": f"Reduce invoice error rate from {st.session_state.om['err']:.0f}% — automate order validation", "module": "Order Management", "timeline": "6-8 weeks", "tier": 1, "because": f"Data: {st.session_state.om['err']:.0f}% error rate"})
        if st.session_state.om["disp"] > 3:
            all_recs.append({"action": f"Reduce dispute rate from {st.session_state.om['disp']:.0f}% — deploy CollectIQ dispute engine", "module": "Order Management", "timeline": "4-6 weeks", "tier": 1, "because": f"Data: {st.session_state.om['disp']:.0f}% dispute rate"})
        if st.session_state.fl["otif"] < INDUSTRIES[industry]["otif_benchmark"]:
            all_recs.append({"action": f"Improve OTIF from {st.session_state.fl['otif']:.0f}% toward {INDUSTRIES[industry]['otif_benchmark']}% benchmark", "module": "Fulfilment & Logistics", "timeline": "6-10 weeks", "tier": 2, "because": f"Data: OTIF below benchmark"})

        # Guaranteed fallback if somehow empty
        if not all_recs:
            all_recs = [
                {"action": "Deploy Revenue Optimizer CFO Dashboard for real-time O2C visibility", "module": "Platform", "timeline": "2-4 weeks", "tier": 1},
                {"action": "Automate invoice generation on shipment confirmation", "module": "Billing & Revenue", "timeline": "4-6 weeks", "tier": 1},
                {"action": "Implement AI-driven collections prioritisation", "module": "Post-Sales & Closure", "timeline": "4-6 weeks", "tier": 1},
                {"action": "Deploy ML ensemble forecasting with external signals", "module": "Demand Forecasting", "timeline": "8-12 weeks", "tier": 2},
                {"action": "Automate multi-channel order ingestion with LLM/OCR", "module": "Order Management", "timeline": "6-10 weeks", "tier": 2},
                {"action": "Implement customer LTV scoring for commercial decisions", "module": "Post-Sales & Closure", "timeline": "6-8 weeks", "tier": 2},
            ]

        # Sort: tier 1 first, then tier 2
        tier1 = [r for r in all_recs if r.get("tier") == 1][:3]
        remaining = [r for r in all_recs if r not in tier1]
        tier2 = [r for r in remaining if r.get("tier") == 2][:3]
        if len(tier2) < 3: tier2.extend([r for r in remaining if r not in tier2][:3 - len(tier2)])
        if len(tier1) < 3: tier1.extend(remaining[:3 - len(tier1)])

        # Render recommendations
        r1col, r2col = st.columns(2)
        with r1col:
            st.markdown('''<div style="background:linear-gradient(135deg,#fef2f2,#fff1f2);border:2px solid #fecaca;border-radius:16px;padding:1.4rem;box-shadow:0 2px 8px rgba(220,38,38,0.08)">
                <div style="display:flex;align-items:center;gap:8px;margin-bottom:1rem">
                    <div style="background:linear-gradient(135deg,#dc2626,#ef4444);width:32px;height:32px;border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:1rem;color:white;font-weight:700">!</div>
                    <div><div style="font-size:0.85rem;font-weight:700;color:#991b1b;letter-spacing:0.02em">FIX NOW</div><div style="font-size:0.68rem;color:#b91c1c">Top 3 highest-impact actions</div></div>
                </div>''',unsafe_allow_html=True)
            if not tier1:
                st.markdown('<div style="font-size:0.82rem;color:#94a3b8;padding:0.5rem 0">No critical bottlenecks detected — your processes are in good shape.</div>',unsafe_allow_html=True)
            for i, rec in enumerate(tier1, 1):
                st.markdown(f'''<div style="background:white;border-radius:10px;padding:0.65rem 0.75rem;margin-bottom:0.4rem;border:1px solid #fecaca"><div style="display:flex;align-items:flex-start;gap:8px"><div style="background:#dc2626;color:white;width:22px;height:22px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:0.68rem;font-weight:700;flex-shrink:0;margin-top:1px">{i}</div><div><div style="font-size:0.85rem;font-weight:600;color:#0f172a;line-height:1.35">{rec["action"]}</div><div style="display:flex;gap:4px;margin-top:0.3rem"><span style="font-size:0.65rem;font-weight:600;padding:2px 8px;border-radius:8px;background:#eff6ff;color:#1d4ed8">{rec.get("module","")}</span><span style="font-size:0.65rem;padding:2px 8px;border-radius:8px;background:#f1f5f9;color:#64748b">⏱ {rec.get("timeline","")}</span></div></div></div></div>''',unsafe_allow_html=True)
            st.markdown("</div>",unsafe_allow_html=True)

        with r2col:
            st.markdown('''<div style="background:linear-gradient(135deg,#eff6ff,#f0f9ff);border:2px solid #bfdbfe;border-radius:16px;padding:1.4rem;box-shadow:0 2px 8px rgba(3,105,161,0.08)">
                <div style="display:flex;align-items:center;gap:8px;margin-bottom:1rem">
                    <div style="background:linear-gradient(135deg,#0369a1,#0ea5e9);width:32px;height:32px;border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:1rem;color:white;font-weight:700">→</div>
                    <div><div style="font-size:0.85rem;font-weight:700;color:#0c4a6e;letter-spacing:0.02em">PLAN NEXT</div><div style="font-size:0.68rem;color:#0369a1">Build on Tier 1 fixes</div></div>
                </div>''',unsafe_allow_html=True)
            if not tier2:
                st.markdown('<div style="font-size:0.82rem;color:#94a3b8;padding:0.5rem 0">No additional improvements identified at this time.</div>',unsafe_allow_html=True)
            for i, rec in enumerate(tier2, 1):
                st.markdown(f'''<div style="background:white;border-radius:10px;padding:0.65rem 0.75rem;margin-bottom:0.4rem;border:1px solid #bfdbfe"><div style="display:flex;align-items:flex-start;gap:8px"><div style="background:#0369a1;color:white;width:22px;height:22px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:0.68rem;font-weight:700;flex-shrink:0;margin-top:1px">{i}</div><div><div style="font-size:0.85rem;font-weight:600;color:#0f172a;line-height:1.35">{rec["action"]}</div><div style="display:flex;gap:4px;margin-top:0.3rem"><span style="font-size:0.65rem;font-weight:600;padding:2px 8px;border-radius:8px;background:#eff6ff;color:#1d4ed8">{rec.get("module","")}</span><span style="font-size:0.65rem;padding:2px 8px;border-radius:8px;background:#f1f5f9;color:#64748b">⏱ {rec.get("timeline","")}</span></div></div></div></div>''',unsafe_allow_html=True)
            st.markdown("</div>",unsafe_allow_html=True)

with tabs[3]:
    if not st.session_state.done: st.info("Complete Setup and click Run Full Analysis.")
    else:
        render_health_banner(show_modules=["Demand Forecasting","Order Management","Order Fulfilment & Logistics","Billing & Revenue Mgmt","Post-Sales & Financial Closure"])
        ai=st.session_state.ai_exec or {}; bl=st.session_state.bl; ps=st.session_state.ps; s=ai.get("health_score",0)
        # AI recommendation
        om=st.session_state.om; fl=st.session_state.fl; dm_all=st.session_state.dm
        o2c_rec = f'Across your full O2C cycle: order error rate is {om["err"]:.0f}% and dispute rate is {om["disp"]:.0f}%, driving downstream billing delays and revenue leakage of {fmtc(bl["leak_total"],ccy,True)}.'
        worst_area = min(st.session_state.mod_scores, key=st.session_state.mod_scores.get)
        worst_score = st.session_state.mod_scores[worst_area]
        o2c_rec += f' Your weakest module is {worst_area} at {worst_score}/100 — prioritise improvements here for the highest cascading impact across the cycle.'
        if fl["otif"] < INDUSTRIES[industry]["otif_benchmark"]: o2c_rec += f' Fulfilment OTIF at {fl["otif"]}% is below benchmark — this directly affects customer satisfaction and repeat orders.'
        if ps["aging"]["90d"] > 10: o2c_rec += f' {ps["aging"]["90d"]}% of receivables past 90 days is a cash risk that needs immediate attention.'
        st.markdown(f'<div style="background:linear-gradient(135deg,#fefce8,#fef3c7);border:2px solid #fde68a;border-radius:14px;padding:1.1rem 1.4rem;margin-bottom:1rem;box-shadow:0 2px 8px rgba(245,158,11,0.08)"><div style="font-size:0.7rem;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;color:#92400e;margin-bottom:0.4rem">📋 AI RECOMMENDATION — O2C PERFORMANCE</div><div style="font-size:0.92rem;color:#78350f;line-height:1.65">{o2c_rec}</div></div>',unsafe_allow_html=True)
        if st.session_state.market_fetched and st.session_state.market_ai:
            ms_t=st.session_state.market_ai.get("market_summary","")
            if ms_t: st.markdown(f'<div class="info-box"><strong>Market Context:</strong> {ms_t}</div>',unsafe_allow_html=True)
        rev=bl["rev"]; leak=bl["leak_total"]; outstd=rev*(ps["aging"]["30d"]+ps["aging"]["60d"]+ps["aging"]["90d"])/100
        c1,c2,c3,c4,c5=st.columns(5)
        with c1: st.markdown(mcard("Total Revenue",fmtc(rev,ccy,True),"Total invoiced","neutral","Sum of all Invoice_Amount_USD in your O2C data","Source: Your uploaded data","metric-card metric-card-green"),unsafe_allow_html=True)
        with c2: st.markdown(mcard("Leakage",fmtc(leak,ccy,True),f"{round(leak/max(rev,1)*100,1)}% of revenue","bad","Discounting 1.8% + Errors + Disputes + Deductions","Source: McKinsey O2C Optimization; Normality SPAN Module 4.4","metric-card metric-card-red"),unsafe_allow_html=True)
        with c3: st.markdown(mcard("Outstanding AR",fmtc(outstd,ccy,True),"Receivables >30d","neutral","Revenue x (% invoices past 30 days)","Source: Calculated from your DSO distribution","metric-card metric-card-amber"),unsafe_allow_html=True)
        with c4: st.markdown(f'<div class="metric-card-dark"><div class="metric-label">Net Recovered</div><div class="metric-value" style="font-size:1.4rem">{fmtc(rev-leak,ccy,True)}</div><div class="mex" style="color:#64748b">Revenue minus all estimated leakage</div></div>',unsafe_allow_html=True)
        with c5:
            reason=ai.get("health_reason","Composite of module scores, data metrics, and maturity")
            st.markdown(f'<div class="metric-card" style="text-align:center"><div class="metric-label">Health</div><div class="metric-value" style="color:{scolor(s)};font-size:2.5rem">{s}</div><div style="font-size:0.75rem;font-weight:600;color:{scolor(s)}">{ai.get("overall_health","")}</div><div class="mex">{reason}</div><div class="msrc">60% data metrics + 40% maturity assessment</div></div>',unsafe_allow_html=True)
        if not bl["cashflow"].empty:
            st.markdown("<br>",unsafe_allow_html=True)
            st.markdown('<div class="section-card"><div class="section-title">Cash Flow Trend — Last 12 Months</div><div class="mex" style="margin-top:-0.5rem;margin-bottom:0.5rem">Values in thousands of USD ($K). Hover to see net position.</div>',unsafe_allow_html=True)
            cf=bl["cashflow"].tail(12).copy()
            cf["Inflow ($K)"] = (cf["Inflow"] / 1000).round(0).astype(int)
            cf["Outflow ($K)"] = (cf["Outflow"] / 1000).round(0).astype(int)
            cf["Net ($K)"] = cf["Inflow ($K)"] - cf["Outflow ($K)"]
            cf["Status"] = cf["Net ($K)"].apply(lambda v: "Surplus" if v >= 0 else "Deficit")
            tt = [alt.Tooltip("Month:N"),alt.Tooltip("Inflow ($K):Q",format=","),alt.Tooltip("Outflow ($K):Q",format=","),alt.Tooltip("Net ($K):Q",format="+,"),alt.Tooltip("Status:N")]
            base = alt.Chart(cf).encode(x=alt.X("Month:N",sort=None,title=None))
            inflow = base.mark_area(opacity=0.3,line=alt.OverlayMarkDef(strokeWidth=2.5),color="#16a34a").encode(y=alt.Y("Inflow ($K):Q",title="$K",axis=alt.Axis(format=",")),tooltip=tt)
            outflow = base.mark_area(opacity=0.3,line=alt.OverlayMarkDef(strokeWidth=2.5),color="#dc2626").encode(y="Outflow ($K):Q",tooltip=tt)
            chart = (inflow + outflow).properties(height=280,width="container").configure_view(strokeWidth=0)
            st.altair_chart(chart, use_container_width=True)
            nt=cf["Net ($K)"].sum()
            st.markdown(f'<div style="display:flex;justify-content:space-between;font-size:0.78rem;color:#64748b"><span><span style="color:#16a34a">━</span> Inflow <span style="color:#dc2626">━</span> Outflow</span><span>Net: <span style="font-family:JetBrains Mono;font-weight:700;color:{"#16a34a" if nt>=0 else "#dc2626"}">${nt:,}K</span></span></div>',unsafe_allow_html=True)
            st.markdown("</div>",unsafe_allow_html=True)
        st.markdown("<br>",unsafe_allow_html=True)
        cs,csm=st.columns([1,2])
        with cs:
            exec_summary = ai.get("executive_summary","")
            if not exec_summary:
                exec_summary = f'Analysis based on uploaded data: Forecast accuracy at {st.session_state.dm["accuracy"]}% ({"above" if st.session_state.dm["accuracy"]>=85 else "below"} 85% target). DSO at {bl["dso"]}d vs {bl["bench"]}d benchmark — {"within range" if bl["gap"]<=0 else f"gap of {bl["gap"]:.0f} days"}. Revenue leakage estimated at {fmtc(leak,ccy)} ({round(leak/max(rev,1)*100,1)}% of revenue). Working capital health score: {ps["score"]}/100. AI-generated insights unavailable — check Gemini API key in environment.'
            st.markdown(f'<div class="section-card"><div class="section-title">Strategic Assessment</div><p style="color:#334155;line-height:1.7;font-size:0.95rem">{exec_summary}</p></div>',unsafe_allow_html=True)
        with csm:
            st.markdown('<div class="section-card"><div class="section-title">Module Health</div>',unsafe_allow_html=True)
            st.markdown('<div class="mex" style="margin-top:-0.5rem;margin-bottom:0.75rem">Blended score: 60% from your data metrics + 40% from your maturity self-assessment. 70+ = Good, 45-69 = At Risk, below 45 = Critical.</div>',unsafe_allow_html=True)
            ms=st.session_state.mod_scores or {}; icons={"Demand Forecasting":"📦","Order Management":"📋","Order Fulfilment & Logistics":"🚚","Billing & Revenue Mgmt":"💰","Post-Sales & Financial Closure":"🏦"}
            mc=st.columns(5)
            for col,(mn,mv) in zip(mc,ms.items()):
                ex="Operating above benchmark" if mv>=70 else "Gaps identified — improvement needed" if mv>=45 else "Critical — significant intervention needed"
                with col: st.markdown(f'<div class="module-card"><div style="font-size:0.63rem;font-weight:600;letter-spacing:0.04em;text-transform:uppercase;color:#64748b">{icons.get(mn,"")} {mn}</div><div style="font-size:1.7rem;font-weight:600;font-family:JetBrains Mono,monospace;color:{scolor(mv)};margin:0.4rem 0">{mv}</div><div class="mod-explain">{ex}</div></div>',unsafe_allow_html=True)
            st.markdown("</div>",unsafe_allow_html=True)
        st.markdown("<br>",unsafe_allow_html=True)
        cl,cr=st.columns(2)
        with cl:
            st.markdown('<div class="section-card"><div class="section-title">Top Risks</div>',unsafe_allow_html=True)
            top_risks = ai.get("top_risks",[])
            if not top_risks:
                # Data-driven fallback risks when AI is unavailable
                fallback_risks = []
                if st.session_state.dm["accuracy"] < 85: fallback_risks.append({"risk":"Forecast accuracy below target","severity":"High","impact":f'Current {st.session_state.dm["accuracy"]}% vs 85% target — leads to excess inventory or stockouts',"module":"Demand Forecasting","why":f'MAPE at {st.session_state.dm["mape"]}% indicates significant forecast error'})
                if bl["gap"] > 5: fallback_risks.append({"risk":"DSO exceeds industry benchmark","severity":"High","impact":f'DSO {bl["dso"]}d vs {bl["bench"]}d benchmark — working capital tied up',"module":"Billing & Revenue","why":f'Gap of {bl["gap"]:.0f} days above benchmark directly impacts cash conversion'})
                if st.session_state.om["err"] > 2: fallback_risks.append({"risk":"Invoice error rate above threshold","severity":"Medium","impact":f'{st.session_state.om["err"]}% errors cascade into disputes and delayed payments',"module":"Order Management","why":"Error rate above 2% APQC target"})
                if st.session_state.fl["otif"] < st.session_state.fl["otif_bench"]: fallback_risks.append({"risk":"OTIF below benchmark","severity":"Medium","impact":f'OTIF {st.session_state.fl["otif"]}% vs {st.session_state.fl["otif_bench"]}% benchmark',"module":"Fulfilment","why":"Below benchmark increases customer churn risk"})
                if ps["aging"]["90d"] >= 10: fallback_risks.append({"risk":"High AR aging beyond 90 days","severity":"High","impact":f'{ps["aging"]["90d"]}% of receivables past 90 days — write-off risk',"module":"Post-Sales","why":"Above 10% threshold per APQC Collections Benchmarks"})
                if not fallback_risks: fallback_risks.append({"risk":"No critical risks detected","severity":"Low","impact":"All metrics within acceptable ranges","module":"All","why":"Data-driven assessment shows healthy performance"})
                top_risks = fallback_risks
            for r in top_risks[:5]:
                sv=r.get("severity","Medium"); bc="risk-high" if sv=="High" else "risk-med" if sv=="Medium" else "risk-low"; why=r.get("why","")
                st.markdown(f'<div class="insight-row"><div><span class="risk-badge {bc}">{sv}</span> <span style="font-size:0.7rem;background:#f1f5f9;padding:2px 8px;border-radius:20px;color:#64748b">{r.get("module","")}</span><div style="font-weight:500;margin-top:0.4rem">{r.get("risk","")}</div><div style="font-size:0.82rem;color:#64748b">{r.get("impact","")}</div><div class="risk-why">Why {sv}: {why}</div></div></div>',unsafe_allow_html=True)
            st.markdown("</div>",unsafe_allow_html=True)
        with cr:
            st.markdown('<div class="section-card"><div class="section-title">Quick Wins</div>',unsafe_allow_html=True)
            quick_wins = ai.get("quick_wins",[])
            if not quick_wins:
                quick_wins = []
                if bl["gap"] > 0: quick_wins.append({"action":"Automate invoice triggering on ePOD confirmation","timeline":"4-6 weeks","expected_impact":f"Reduce DSO by {min(bl['gap'],10):.0f} days","module":"BillingEngine"})
                if st.session_state.om["err"] > 2: quick_wins.append({"action":"Deploy AI order validation before ERP entry","timeline":"6-8 weeks","expected_impact":f"Reduce error rate from {st.session_state.om['err']}% to <2%","module":"OrderValidate"})
                if st.session_state.dm["accuracy"] < 85: quick_wins.append({"action":"Implement ensemble ML forecasting with context signals","timeline":"8-12 weeks","expected_impact":f"Improve forecast accuracy from {st.session_state.dm['accuracy']}% toward 85%+","module":"ForecastEngine"})
                quick_wins.append({"action":"Launch CFO dashboard for real-time O2C visibility","timeline":"2-4 weeks","expected_impact":"Eliminate manual reporting; management by exception","module":"Revenue Optimizer Dashboard"})
                quick_wins.append({"action":"Activate predictive collections for high-DSO customers","timeline":"4-6 weeks","expected_impact":"Proactive dunning on at-risk invoices","module":"CollectIQ"})
            for i,qw in enumerate(quick_wins[:5],1):
                st.markdown(f'<div class="insight-row"><div style="background:#0a1628;border-radius:50%;width:24px;height:24px;display:flex;align-items:center;justify-content:center;font-size:0.75rem;font-weight:600;color:white;flex-shrink:0">{i}</div><div><div style="font-weight:500">{qw.get("action","")}</div><div style="font-size:0.8rem;color:#64748b">⏱ {qw.get("timeline","")} · 📈 {qw.get("expected_impact","")}</div><span style="font-size:0.7rem;background:#e0f2fe;color:#0369a1;padding:2px 8px;border-radius:20px">{qw.get("module","")}</span></div></div>',unsafe_allow_html=True)
            st.markdown("</div>",unsafe_allow_html=True)

with tabs[2]:
    if not st.session_state.done: st.info("Upload data and Run Full Analysis.")
    else:
        render_health_banner(show_modules=["Demand Forecasting"])
        # Year filter
        fc_years = get_demand_years(st.session_state.fc_df)
        sel_yr = st.radio("📅 Period", options=fc_years, horizontal=True, key="fc_yr")
        fc_filtered = filter_demand_by_year(st.session_state.fc_df, sel_yr)
        dm = calc_demand(fc_filtered) if sel_yr != "Last 3 Years" else st.session_state.dm
        ob=INDUSTRIES[industry]["otif_benchmark"]
        # AI Recommendation
        yr_label = f" ({sel_yr})" if sel_yr != "Last 3 Years" else " (All years)"
        fc_rec = f'Forecast accuracy is {dm["accuracy"]:.1f}%{yr_label} with MAPE of {dm["mape"]:.1f}%.'
        if dm["bias"] < -5: fc_rec += f' You are systematically under-forecasting (bias {dm["bias"]:+.1f}%) — demand is consistently higher than planned, creating stockout risk. Consider adding promotional uplift signals and increasing safety stock on high-variance SKUs.'
        elif dm["bias"] > 5: fc_rec += f' You are systematically over-forecasting (bias {dm["bias"]:+.1f}%) — excess inventory is tying up working capital. Tighten your demand signal inputs and review whether historical trends are being over-weighted.'
        else: fc_rec += f' Forecast bias is well-controlled at {dm["bias"]:+.1f}% — focus on reducing MAPE through SKU-level model tuning.'
        worst_sku = dm["sku"].sort_values("MAPE",ascending=False).iloc[0] if len(dm["sku"])>0 else None
        if worst_sku is not None and worst_sku["MAPE"] > 20: fc_rec += f' {worst_sku["SKU"]} is your worst performer at {worst_sku["MAPE"]:.0f}% MAPE — isolate this SKU for promotion-adjusted or external-signal-enhanced modelling.'
        if dm["accuracy"] < 85: fc_rec += f' To reach the 85% accuracy target, invest in ML ensemble models with context signals (weather, promotions, macro trends) rather than relying on historical averages alone.'
        st.markdown(f'<div style="background:linear-gradient(135deg,#f0fdf4,#dcfce7);border:2px solid #86efac;border-radius:14px;padding:1.1rem 1.4rem;margin-bottom:1rem;box-shadow:0 2px 8px rgba(22,163,74,0.08)"><div style="font-size:0.7rem;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;color:#16a34a;margin-bottom:0.4rem">📦 AI RECOMMENDATION — DEMAND FORECASTING</div><div style="font-size:0.92rem;color:#14532d;line-height:1.65">{fc_rec}</div></div></div>',unsafe_allow_html=True)
        c1,c2,c3,c4=st.columns(4)
        with c1: st.markdown(mcard("Forecast Accuracy",f'{dm["accuracy"]}%',"Target: 85-90%","good" if dm["accuracy"]>=85 else "bad","Formula: 100 - MAPE. Higher = closer to actual demand.","Target: Normality SoW (65%→90%+); Expert Interview confirmed no tracking","metric-card metric-card-blue"),unsafe_allow_html=True)
        with c2: st.markdown(mcard("Variance (Bias)",f'{abs(dm["bias"]):.1f}%',"Over-forecast" if dm["bias"]>5 else "Under-forecast" if dm["bias"]<-5 else "Stable","bad" if abs(dm["bias"])>5 else "good","(Actual - Forecast) / Actual. Positive = excess inventory risk.","Target: ±5%. Source: OTexts Forecasting Principles & Practice","metric-card"),unsafe_allow_html=True)
        with c3: st.markdown(f'<div class="metric-card-dark"><div class="metric-label">MAPE</div><div class="metric-value">{dm["mape"]}%</div><div class="mex" style="color:#64748b">Mean Absolute % Error. Avg |Actual-Forecast|/Actual.</div><div class="msrc" style="color:#64748b">Target: below 15%. Source: OTexts; M4 Competition benchmarks</div></div>',unsafe_allow_html=True)
        with c4: st.markdown(mcard("OTIF Rate",f'{dm["otif"]}%',f'Bench: {ob}%',"good" if dm["otif"]>=ob else "bad","Orders OTIF / Orders Placed x 100.","Bench: McKinsey OTIF Consumer Sector (2019); Walmart mandates 98%","metric-card metric-card-green" if dm["otif"]>=ob else "metric-card metric-card-red"),unsafe_allow_html=True)
        st.markdown("<br>",unsafe_allow_html=True)
        cl,cr=st.columns([2,1])
        with cl:
            st.markdown('<div class="section-card"><div class="section-title">Forecast vs Actuals</div><div class="mex" style="margin-top:-0.5rem;margin-bottom:1rem">Monthly aggregated actual demand vs forecasted (units). Hover to see variance.</div>',unsafe_allow_html=True)
            vd=dm["variance"]
            if not vd.empty:
                vc = vd[["Month","Actual","Forecast"]].copy()
                vc["Actual"] = vc["Actual"].round(0).astype(int)
                vc["Forecast"] = vc["Forecast"].round(0).astype(int)
                vc["Variance"] = vc["Actual"] - vc["Forecast"]
                vc["Status"] = vc["Variance"].apply(lambda v: "Surplus" if v >= 0 else "Deficit")
                tt = [alt.Tooltip("Month:N"),alt.Tooltip("Actual:Q",format=","),alt.Tooltip("Forecast:Q",format=","),alt.Tooltip("Variance:Q",title="Variance (A−F)",format="+,"),alt.Tooltip("Status:N")]
                base = alt.Chart(vc).encode(x=alt.X("Month:N",sort=None,title=None))
                act_line = base.mark_line(strokeWidth=2.5,point=alt.OverlayMarkDef(size=40),color="#0f172a").encode(y=alt.Y("Actual:Q",title="Units",axis=alt.Axis(format=",")),tooltip=tt)
                fc_line = base.mark_line(strokeWidth=2.5,point=alt.OverlayMarkDef(size=40),color="#16a34a").encode(y="Forecast:Q",tooltip=tt)
                chart = (act_line + fc_line).properties(height=260,width="container").configure_view(strokeWidth=0)
                st.altair_chart(chart, use_container_width=True)
                st.markdown('<div style="font-size:0.78rem;color:#64748b"><span style="color:#0f172a">━</span> Actual <span style="color:#16a34a">━</span> Forecast</div>',unsafe_allow_html=True)
            st.markdown("</div>",unsafe_allow_html=True)
        with cr:
            st.markdown('<div class="section-card"><div class="section-title">Variance Analysis</div><div class="mex" style="margin-top:-0.5rem;margin-bottom:0.75rem">Difference = Actual minus Forecast (units). Deviation = Variance as % of Forecast.</div>',unsafe_allow_html=True)
            for _,row in dm["variance"].tail(6).iterrows():
                vp=row["Variance_Pct"]; vc="var-pos" if vp>=0 else "var-neg"
                st.markdown(f'<div class="var-card"><div class="var-label">{row["Month"]} <span class="var-badge">Variance</span></div><div class="var-row"><span>Difference</span><span class="{vc}">{row["Variance"]:+,.0f} units</span></div><div class="var-row"><span>Deviation</span><span class="{vc}">{vp:+.1f}%</span></div></div>',unsafe_allow_html=True)
            st.markdown("</div>",unsafe_allow_html=True)
        st.markdown("<br>",unsafe_allow_html=True)
        cl2,cr2=st.columns(2)
        with cl2:
            st.markdown('<div class="section-card"><div class="section-title">SKU Performance</div><div class="mex" style="margin-top:-0.5rem;margin-bottom:0.75rem">Per-SKU accuracy = 100 - SKU MAPE. Green: 70+, Amber: 45-69, Red: below 45.</div>',unsafe_allow_html=True)
            for _,row in dm["sku"].sort_values("Accuracy",ascending=False).iterrows():
                c=scolor(row["Accuracy"])
                st.markdown(f'<div style="margin-bottom:1rem"><div style="display:flex;justify-content:space-between;font-size:0.85rem;margin-bottom:3px"><span style="font-weight:500">{row["SKU"]}</span><span style="color:{c};font-family:JetBrains Mono,monospace;font-weight:500">{row["Accuracy"]}%</span></div><div class="progress-bar-bg"><div class="progress-bar-fill" style="width:{min(100,row["Accuracy"])}%;background:{c}"></div></div><div style="font-size:0.75rem;color:#94a3b8;margin-top:3px">MAPE: {row["MAPE"]}% Bias: {row["Bias"]:+.1f}%</div></div>',unsafe_allow_html=True)
            st.markdown("</div>",unsafe_allow_html=True)
        with cr2:
            if st.session_state.market_fetched and st.session_state.market_ai:
                st.markdown('<div class="section-card"><div class="section-title">External Demand Signals</div><div class="mex" style="margin-top:-0.5rem;margin-bottom:0.75rem">Live signals from RSS, World Bank, Google Trends — AI-interpreted as potential forecast adjustments.</div>',unsafe_allow_html=True)
                for sig in st.session_state.market_ai.get("demand_signals",[])[:4]:
                    st.markdown(f'<div class="news-card"><div style="font-weight:500;font-size:0.9rem">{sig.get("signal","")}</div><div style="font-size:0.78rem;color:#64748b;margin-top:0.2rem">Source: {sig.get("source","")} | Impact: {sig.get("impact","")}</div><div style="font-size:0.82rem;color:#0369a1;margin-top:0.3rem">Adjustment: {sig.get("forecast_adjustment","")}</div></div>',unsafe_allow_html=True)
                st.markdown("</div>",unsafe_allow_html=True)
            else: st.markdown('<div class="section-card"><div class="section-title">External Demand Signals</div><div class="upload-hint">Click Fetch Market Intel in Setup.</div></div>',unsafe_allow_html=True)

        # ─── ORDER MANAGEMENT ───
        st.markdown('<div style="margin-top:2rem;margin-bottom:0.5rem;font-size:0.65rem;font-weight:700;letter-spacing:0.15em;text-transform:uppercase;color:#0369a1;padding:6px 0;border-top:2px solid #0369a1">ORDER MANAGEMENT</div>',unsafe_allow_html=True)
    if st.session_state.done:
        om=st.session_state.om; bc=INDUSTRIES[industry]["cycle_benchmark"]
        c1,c2,c3,c4=st.columns(4)
        with c1: st.markdown(mcard("Order Cycle",f'{om["cycle"]}d',f'Bench: {bc}d',"good" if om["cycle"]<=bc else "bad","Avg days from Order_Date to Invoice_Date.",f"Bench: {bc}d for {industry}. Source: APQC O2C Benchmarks","metric-card metric-card-blue"),unsafe_allow_html=True)
        with c2: st.markdown(mcard("Error Rate",f'{om["err"]}%',"Target: <2%","good" if om["err"]<2 else "bad","% of orders with Invoice_Errors = 1.","Target: APQC Benchmarks; Expert Interview flagged portal failures","metric-card metric-card-green" if om["err"]<2 else "metric-card metric-card-red"),unsafe_allow_html=True)
        with c3: st.markdown(mcard("Dispute Rate",f'{om["disp"]}%',"Target: <5%","good" if om["disp"]<5 else "bad","% of orders flagged as Disputed = 1.","Target: <5%. Source: Normality SPAN Module 4.2","metric-card metric-card-green" if om["disp"]<5 else "metric-card metric-card-amber"),unsafe_allow_html=True)
        with c4: st.markdown(mcard("Amendments",f'{om["amend"]}%',"Low" if om["amend"]<10 else "High churn","good" if om["amend"]<10 else "bad","% of orders with Amendment_Flag = 1.","Expert Interview: order changes are frequent and disruptive in CPG","metric-card metric-card-green" if om["amend"]<10 else "metric-card metric-card-red"),unsafe_allow_html=True)
        st.markdown("<br>",unsafe_allow_html=True)
        st.markdown('<div class="section-card"><div class="section-title">Pain Points & AI Solutions</div><div class="mex" style="margin-top:-0.5rem;margin-bottom:0.75rem">Common challenges identified in SEA CPG expert interviews, mapped to Revenue Optimizer AI solutions.</div>',unsafe_allow_html=True)
        for t,p,f in [("Manual order entry",f"Orders via email/phone need manual ERP entry, causing {om['err']}% error rate.","AI auto-capture: reads order emails/PDFs, populates ERP for human review."),("Amendment chaos",f"{om['amend']}% amendment rate disrupts production and fulfilment planning.","Amendment window enforcement with auto customer notification after cutoff."),("Validation gaps","Incomplete data flows downstream to billing errors and disputes.","Real-time AI validation: pricing, inventory, credit check before order confirmation."),("No real-time visibility","Teams manually check order status across disconnected systems.","Order control tower: unified lifecycle dashboard from receipt to delivery.")]:
            st.markdown(f'<div style="padding:0.75rem 0;border-bottom:1px solid #f1f5f9"><div style="font-weight:500;font-size:0.9rem;color:#0a1628">{t}</div><div style="font-size:0.82rem;color:#64748b;margin-top:0.2rem">{p}</div><div style="font-size:0.82rem;color:#16a34a;margin-top:0.3rem;background:#f0fdf4;padding:4px 8px;border-radius:6px">{f}</div></div>',unsafe_allow_html=True)
        st.markdown("</div>",unsafe_allow_html=True)
        # --- OrderIngest Hub Simulation ---
        if st.session_state.order_ingest:
            oi = st.session_state.order_ingest
            st.markdown("<br>",unsafe_allow_html=True)
            st.markdown('<div class="section-card"><div class="section-title">OrderIngest Hub — AI Order Parsing Simulation</div><div class="mex" style="margin-top:-0.5rem;margin-bottom:0.75rem">Simulates LLM/OCR processing of inbound purchase orders from multiple channels. Confidence score determines auto-parse vs human review routing. Source: OrderIngest Hub (Normality Revenue Optimizer).</div>',unsafe_allow_html=True)
            oc1,oc2,oc3,oc4=st.columns(4)
            with oc1: st.markdown(mcard("Auto-Parse Rate",f'{oi["auto_rate"]}%',"Target: >80%","good" if oi["auto_rate"]>=80 else "bad","% of orders parsed without human intervention.","Source: OrderIngest Hub — OCR/NLP Extractor","metric-card metric-card-green" if oi["auto_rate"]>=80 else "metric-card metric-card-amber"),unsafe_allow_html=True)
            with oc2: st.markdown(mcard("Avg Confidence",f'{oi["avg_confidence"]}%',"AI extraction confidence","good" if oi["avg_confidence"]>=80 else "neutral","Mean confidence score across all parsed orders.","LLM Parser + AI Gap Fill module","metric-card metric-card-blue"),unsafe_allow_html=True)
            with oc3: st.markdown(mcard("Channels Active",f'{oi["channels_active"]}',"Multi-channel","neutral","Number of distinct inbound channels processed.","EDI, Email, Portal, WhatsApp, Fax — unified ingestion","metric-card"),unsafe_allow_html=True)
            with oc4: st.markdown(mcard("Orders Processed",f'{len(oi["orders"])}',"Live queue","neutral","Total orders in current processing batch.","OrderIngest Hub — Live Dashboard","metric-card"),unsafe_allow_html=True)
            st.markdown("<br>",unsafe_allow_html=True)
            for o in oi["orders"][:8]:
                conf_co = "#16a34a" if o["confidence"] >= 85 else "#f59e0b" if o["confidence"] >= 70 else "#dc2626"
                st_cls = "risk-low" if o["status"] == "Auto-Parsed" else "risk-med" if o["status"] == "Human Review" else "risk-high"
                missing_txt = f' · Missing: {", ".join(o["missing_fields"])}' if o["missing_fields"] else ""
                st.markdown(f'<div style="display:flex;justify-content:space-between;align-items:center;padding:0.6rem 0;border-bottom:1px solid #f1f5f9"><div><span style="font-weight:500;font-size:0.85rem">{o["po_id"]}</span> <span style="font-size:0.75rem;color:#94a3b8">· {o["customer"]} · {o["channel"]}</span><div style="font-size:0.75rem;color:#64748b;margin-top:2px">{o["fields_extracted"]}/{o["fields_total"]} fields · {o["processing_time"]}{missing_txt}</div></div><div style="display:flex;align-items:center;gap:8px"><span style="font-family:JetBrains Mono,monospace;font-size:0.82rem;font-weight:600;color:{conf_co}">{o["confidence"]}%</span><span class="risk-badge {st_cls}">{o["status"]}</span></div></div>',unsafe_allow_html=True)
            st.markdown("</div>",unsafe_allow_html=True)

        # ─── ORDER FULFILMENT & LOGISTICS ───
        st.markdown('<div style="margin-top:2rem;margin-bottom:0.5rem;font-size:0.65rem;font-weight:700;letter-spacing:0.15em;text-transform:uppercase;color:#b45309;padding:6px 0;border-top:2px solid #b45309">ORDER FULFILMENT & LOGISTICS</div>',unsafe_allow_html=True)
    if st.session_state.done:
        fl=st.session_state.fl
        c1,c2,c3,c4=st.columns(4)
        with c1: st.markdown(mcard("OTIF",f'{fl["otif"]}%',f'Bench: {fl["otif_bench"]}%',"good" if fl["otif"]>=fl["otif_bench"] else "bad","Avg of OTIF_Flag x 100. On-Time In-Full delivery rate.",f"Bench: McKinsey OTIF Consumer Sector (2019). Walmart mandates 98%.","metric-card metric-card-blue"),unsafe_allow_html=True)
        with c2: st.markdown(mcard("Fulfilment Cycle",f'{fl["ful_days"]}d',f'Bench: {fl["ful_bench"]}d',"good" if fl["ful_days"]<=fl["ful_bench"] else "bad","Avg Fulfilment_Days from order to shipment dispatch.",f"Bench: {fl['ful_bench']}d for {industry}. Source: APQC Benchmarks","metric-card metric-card-green" if fl["ful_days"]<=fl["ful_bench"] else "metric-card metric-card-red"),unsafe_allow_html=True)
        with c3: st.markdown(mcard("Returns",f'{fl["return_rate"]}%',"Target: <3%","good" if fl["return_rate"]<3 else "bad","Avg Return_Flag x 100. Shelf life rejections are key CPG driver.","Expert Interview: expiry returns can cost more than the goods themselves","metric-card metric-card-green" if fl["return_rate"]<3 else "metric-card metric-card-amber"),unsafe_allow_html=True)
        with c4: st.markdown(mcard("Partial Shipments",f'{fl["partial"]}%',"Incomplete deliveries","bad" if fl["partial"]>10 else "good","100 - OTIF %. Orders not delivered in full.","Impacts OTIF score and customer satisfaction. Source: Normality SPAN Analysis","metric-card metric-card-green" if fl["partial"]<10 else "metric-card metric-card-red"),unsafe_allow_html=True)
        if st.session_state.market_fetched and st.session_state.market_ai:
            st.markdown("<br>",unsafe_allow_html=True)
            st.markdown('<div class="section-card"><div class="section-title">Supply Risk Radar</div><div class="mex" style="margin-top:-0.5rem;margin-bottom:0.75rem">Live external threats to fulfilment from regional news, World Bank, and Google Trends. AI interprets severity and suggests mitigations.</div>',unsafe_allow_html=True)
            for r in st.session_state.market_ai.get("supply_risks",[])[:4]:
                sv=r.get("severity","Medium"); bc2="risk-high" if sv=="High" else "risk-med" if sv=="Medium" else "risk-low"
                st.markdown(f'<div class="news-card"><span class="risk-badge {bc2}">{sv}</span><div style="font-weight:500;font-size:0.9rem;margin-top:0.3rem">{r.get("risk","")}</div><div style="font-size:0.78rem;color:#64748b">Source: {r.get("source","")} | Mitigation: {r.get("mitigation","")}</div></div>',unsafe_allow_html=True)
            st.markdown("</div>",unsafe_allow_html=True)
        if st.session_state.market_fetched and st.session_state.news:
            st.markdown("<br>",unsafe_allow_html=True)
            st.markdown('<div class="section-card"><div class="section-title">Regional News</div>',unsafe_allow_html=True)
            for a in (st.session_state.news or [])[:5]:
                tags="".join([f'<span class="news-tag">{k}</span>' for k in a["keywords"]])
                st.markdown(f'<div class="news-card"><div style="font-size:0.9rem;font-weight:500">{a["title"]}</div><div style="font-size:0.75rem;color:#94a3b8">{a["source"]} {a["published"]}</div><div style="margin-top:0.3rem">{tags}</div></div>',unsafe_allow_html=True)
            st.markdown("</div>",unsafe_allow_html=True)

with tabs[4]:
    if not st.session_state.done: st.info("Upload data and Run Full Analysis.")
    else:
        render_health_banner(show_modules=["Billing & Revenue Mgmt","Post-Sales & Financial Closure"])
        # Year filter
        o2c_years = get_available_years(st.session_state.o2c_df)
        sel_yr_cfo = st.radio("📅 Period", options=o2c_years, horizontal=True, key="cfo_yr")
        o2c_filtered = filter_by_year(st.session_state.o2c_df, sel_yr_cfo)
        bl = calc_billing(o2c_filtered, industry) if sel_yr_cfo != "Last 3 Years" else st.session_state.bl
        lpct=round((bl["leak_total"]/max(bl["rev"],1))*100,1)
        # AI Recommendation
        yr_label = f" ({sel_yr_cfo})" if sel_yr_cfo != "Last 3 Years" else " (All years)"
        cfo_rec = f'DSO is {bl["dso"]:.0f} days{yr_label}, {"on target — maintain current collections discipline" if bl["gap"]<=0 else f"{bl["gap"]:.0f} days above the {bl["bench"]}d benchmark — each excess day traps working capital"}.'
        cfo_rec += f' Revenue leakage at {fmtc(bl["leak_total"],ccy,True)} ({lpct}% of revenue) — '
        if lpct > 3: cfo_rec += 'this exceeds the 3% threshold. Deploy PriceGuard to enforce pricing discipline from quote to invoice, and automate invoice generation via BillingEngine to close the billing delay gap.'
        elif lpct > 1.5: cfo_rec += 'within range but recoverable. Focus on discount governance and invoice accuracy — these two alone typically recover 30-50% of leakage.'
        else: cfo_rec += 'well-controlled. Shift focus to collections optimisation and working capital efficiency.'
        if bl["err"] > 5: cfo_rec += f' Invoice error rate at {bl["err"]:.0f}% is cascading into disputes — fixing upstream order validation would reduce this significantly.'
        st.markdown(f'<div style="background:linear-gradient(135deg,#eff6ff,#dbeafe);border:2px solid #93c5fd;border-radius:14px;padding:1.1rem 1.4rem;margin-bottom:1rem;box-shadow:0 2px 8px rgba(3,105,161,0.08)"><div style="font-size:0.7rem;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;color:#1e40af;margin-bottom:0.4rem">💰 AI RECOMMENDATION — BILLING & REVENUE</div><div style="font-size:0.92rem;color:#1e3a5f;line-height:1.65">{cfo_rec}</div></div>',unsafe_allow_html=True)
        c1,c2,c3,c4=st.columns(4)
        with c1: st.markdown(mcard("DSO",f'{bl["dso"]}d',f'{bl["gap"]:+.0f}d vs {bl["bench"]}d',"good" if bl["gap"]<=0 else "bad","Avg DSO_Days. Days from invoice to payment.",f"Bench: {bl['bench']}d for {industry}. Source: APQC; McKinsey O2C Optimization","metric-card metric-card-blue"),unsafe_allow_html=True)
        with c2: st.markdown(mcard("Invoice Errors",f'{bl["err"]}%',"Target: <2%","good" if bl["err"]<2 else "bad","% invoices flagged with errors.","Target: APQC. Expert Interview: portal submission failures cause delays","metric-card metric-card-green" if bl["err"]<2 else "metric-card metric-card-red"),unsafe_allow_html=True)
        with c3: st.markdown(mcard("Disputes",f'{bl["disp"]}%',"Target: <5%","good" if bl["disp"]<5 else "bad","% invoices disputed. Often from late order amendments.","Source: Normality SPAN Module 4.2; Expert Interview on rebate mismatches","metric-card metric-card-green" if bl["disp"]<5 else "metric-card metric-card-amber"),unsafe_allow_html=True)
        with c4: st.markdown(f'<div class="metric-card-dark"><div class="metric-label" style="color:#f87171">Revenue Leakage</div><div class="metric-value" style="font-size:1.4rem">{lpct}%</div><div style="font-size:0.78rem;color:#94a3b8;margin-top:0.3rem">{fmtc(bl["leak_total"],ccy)}</div><div class="mex" style="color:#64748b">Disc 1.8% + Errors {bl["err"]}%x2.5% + Disputes {bl["disp"]}%x5% + Deductions 0.8%</div><div class="msrc" style="color:#64748b">Source: McKinsey O2C (1.5-3% typical); Normality SPAN Module 4.4</div></div>',unsafe_allow_html=True)
        # Monthly receivable collections chart from actual data
        st.markdown("<br>",unsafe_allow_html=True)
        st.markdown('<div class="section-card"><div class="section-title">Monthly Collections — Actual vs Expected</div><div class="mex" style="margin-top:-0.5rem;margin-bottom:1rem">Values in thousands of USD ($K). Hover to see collection gap per month.</div>',unsafe_allow_html=True)
        try:
            cf_data = o2c_filtered.copy()
            cf_data["Pay_Month"] = pd.to_datetime(cf_data["Payment_Date"]).dt.to_period("M").astype(str)
            cf_data["Inv_Month"] = pd.to_datetime(cf_data["Invoice_Date"]).dt.to_period("M").astype(str)
            collected = cf_data.groupby("Pay_Month")["Invoice_Amount_USD"].sum().rename("Collected")
            invoiced = cf_data.groupby("Inv_Month")["Invoice_Amount_USD"].sum().rename("Invoiced")
            monthly = pd.DataFrame({"Collected": collected, "Invoiced": invoiced}).fillna(0).sort_index().tail(12)
            if len(monthly) > 2:
                mk = monthly.reset_index(); mk.columns = ["Month","Collected","Invoiced"]
                mk["Collected ($K)"] = (mk["Collected"] / 1000).round(0).astype(int)
                mk["Invoiced ($K)"] = (mk["Invoiced"] / 1000).round(0).astype(int)
                mk["Gap ($K)"] = mk["Invoiced ($K)"] - mk["Collected ($K)"]
                mk["Status"] = mk["Gap ($K)"].apply(lambda v: "Under-collected" if v > 0 else "Over-collected")
                tt = [alt.Tooltip("Month:N"),alt.Tooltip("Invoiced ($K):Q",format=","),alt.Tooltip("Collected ($K):Q",format=","),alt.Tooltip("Gap ($K):Q",format="+,"),alt.Tooltip("Status:N")]
                base = alt.Chart(mk).encode(x=alt.X("Month:N",sort=None,title=None))
                inv_line = base.mark_line(strokeWidth=2.5,point=alt.OverlayMarkDef(size=40),color="#0369a1").encode(y=alt.Y("Invoiced ($K):Q",title="$K",axis=alt.Axis(format=",")),tooltip=tt)
                col_line = base.mark_line(strokeWidth=2.5,point=alt.OverlayMarkDef(size=40),color="#16a34a").encode(y="Collected ($K):Q",tooltip=tt)
                chart = (inv_line + col_line).properties(height=260,width="container").configure_view(strokeWidth=0)
                st.altair_chart(chart, use_container_width=True)
                gap_pct = round((1 - monthly["Collected"].sum() / max(monthly["Invoiced"].sum(),1)) * 100, 1)
                st.markdown(f'<div style="display:flex;justify-content:space-between;font-size:0.78rem;color:#64748b"><span><span style="color:#0369a1">━</span> Invoiced <span style="color:#16a34a">━</span> Collected</span><span>Efficiency: <span style="font-weight:600;color:{"#16a34a" if gap_pct<5 else "#f59e0b" if gap_pct<15 else "#dc2626"}">{100-gap_pct}%</span> — ${(monthly["Invoiced"].sum()-monthly["Collected"].sum())/1000:,.0f}K gap</span></div>',unsafe_allow_html=True)
        except: pass
        st.markdown("</div>",unsafe_allow_html=True)
        st.markdown("<br>",unsafe_allow_html=True)
        cl,cr=st.columns([3,2])
        with cl:
            st.markdown('<div class="section-card"><div class="section-title">Revenue Leakage Waterfall</div><div class="mex" style="margin-top:-0.5rem;margin-bottom:0.75rem">How revenue erodes by leakage type. Multipliers from McKinsey O2C benchmarks and Normality SPAN analysis.</div>',unsafe_allow_html=True)
            rev=bl["rev"]; net=rev-bl["leak_total"]
            for lb,v,co,d in [("Gross Revenue",rev,"#0a1628","Total invoiced revenue"),("Discounting",-bl["leak_disc"],"#dc2626","1.8% of revenue — rogue discounts (McKinsey O2C benchmark)"),("Invoice Errors",-bl["leak_inv"],"#ea580c",f'{bl["err"]}% error rate x 2.5% cost per error (APQC)'),("Disputes",-bl["leak_disp"],"#f59e0b",f'{bl["disp"]}% dispute rate x 5% cost (Normality SPAN 4.2)'),("Deductions",-bl["leak_ded"],"#8b5cf6","0.8% — out-of-terms deductions (Expert Interview)"),("Net Recovered",net,"#16a34a","After all leakage types addressed")]:
                neg=v<0; dv=f"-{fmtc(abs(v),ccy)}" if neg else fmtc(v,ccy); pct=min(100,abs(v)/max(rev,1)*100)
                st.markdown(f'<div style="margin-bottom:0.75rem"><div style="display:flex;justify-content:space-between;font-size:0.85rem;margin-bottom:4px"><span style="font-weight:500">{lb}</span><span style="font-family:JetBrains Mono,monospace;font-weight:600;color:{co}">{dv}</span></div><div class="progress-bar-bg"><div class="progress-bar-fill" style="width:{pct}%;background:{co}"></div></div><div style="font-size:0.68rem;color:#94a3b8;margin-top:3px">{d}</div></div>',unsafe_allow_html=True)
            st.markdown("</div>",unsafe_allow_html=True)
        with cr:
            st.markdown('<div class="section-card"><div class="section-title">Customer DSO Risk</div><div class="mex" style="margin-top:-0.5rem;margin-bottom:0.75rem">High: DSO > 1.4x benchmark. Medium: > 1.1x benchmark. Low: at or below.</div>',unsafe_allow_html=True)
            for _,row in bl["cust"].head(8).iterrows():
                r=row["Risk"]; rc="risk-high" if r=="High" else "risk-med" if r=="Medium" else "risk-low"
                st.markdown(f'<div style="display:flex;justify-content:space-between;align-items:center;padding:0.5rem 0;border-bottom:1px solid #f1f5f9"><span style="font-size:0.85rem;font-weight:500">{row["Customer"]}</span><span><span style="font-family:JetBrains Mono,monospace;font-size:0.85rem;margin-right:8px">{row["Avg_DSO"]}d</span><span class="risk-badge {rc}">{r}</span></span></div>',unsafe_allow_html=True)
            st.markdown("</div>",unsafe_allow_html=True)
        # --- BillingEngine Auto-Invoice Simulation ---
        if st.session_state.invoice_demo:
            iv = st.session_state.invoice_demo
            st.markdown("<br>",unsafe_allow_html=True)
            st.markdown('<div class="section-card"><div class="section-title">BillingEngine — Auto-Invoice Trigger Simulation</div><div class="mex" style="margin-top:-0.5rem;margin-bottom:0.75rem">Simulates automated invoice generation triggered by ePOD confirmation. Each invoice runs through Data Validation Layer (qty vs ePOD, price vs PriceGuard, tax, doc requirements) before release. Source: BillingEngine (Normality Revenue Optimizer).</div>',unsafe_allow_html=True)
            iv1,iv2,iv3=st.columns(3)
            with iv1: st.markdown(mcard("Auto-Generated",f'{iv["auto_rate"]}%',"Touchless invoices","good" if iv["auto_rate"]>=70 else "bad","% invoices passing all validation checks automatically.","BillingEngine — Auto Invoice Trigger. Target: >90% touchless","metric-card metric-card-green" if iv["auto_rate"]>=70 else "metric-card metric-card-amber"),unsafe_allow_html=True)
            with iv2: st.markdown(mcard("Avg Time (After)",f'{iv["avg_time_after"]} hrs',"With BillingEngine","good","Time from shipment to invoice with automation.","BillingEngine fires on ePOD confirmation — zero manual step","metric-card metric-card-blue"),unsafe_allow_html=True)
            with iv3: st.markdown(mcard("Avg Time (Before)",f'{iv["avg_time_before"]} hrs',"Manual process","bad","Typical manual invoicing delay in SEA mid-market.","Kleen-Pak CFO: invoicing triggered manually after logistics email","metric-card metric-card-red"),unsafe_allow_html=True)
            st.markdown("<br>",unsafe_allow_html=True)
            for inv in iv["invoices"][:8]:
                st_cls = "risk-low" if inv["status"] == "Auto-Generated" else "risk-high"
                checks_html = " ".join([f'<span style="font-size:0.65rem;background:#dcfce7;color:#166534;padding:1px 6px;border-radius:10px;margin-right:2px">✓ {c}</span>' for c in inv["checks_passed"]])
                fail_html = " ".join([f'<span style="font-size:0.65rem;background:#fee2e2;color:#991b1b;padding:1px 6px;border-radius:10px;margin-right:2px">✗ {c}</span>' for c in inv["checks_failed"]])
                st.markdown(f'<div style="padding:0.6rem 0;border-bottom:1px solid #f1f5f9"><div style="display:flex;justify-content:space-between;align-items:center"><div><span style="font-weight:500;font-size:0.85rem">{inv["invoice_id"]}</span> <span style="font-size:0.75rem;color:#94a3b8">· {inv["customer"]} · {inv["trigger"]}</span></div><div style="display:flex;align-items:center;gap:8px"><span style="font-family:JetBrains Mono,monospace;font-size:0.82rem">{fmtc(inv["amount_usd"],ccy)}</span><span class="risk-badge {st_cls}">{inv["status"]}</span></div></div><div style="margin-top:4px">{checks_html}{fail_html}</div><div style="font-size:0.7rem;color:#94a3b8;margin-top:2px">⏱ {inv["time_to_invoice"]} (was: {inv["before_time"]})</div></div>',unsafe_allow_html=True)
            st.markdown("</div>",unsafe_allow_html=True)

        # ─── POST-SALES & WORKING CAPITAL ───
        st.markdown('<div style="margin-top:2rem;margin-bottom:0.5rem;font-size:0.65rem;font-weight:700;letter-spacing:0.15em;text-transform:uppercase;color:#7c3aed;padding:6px 0;border-top:2px solid #7c3aed">POST-SALES & WORKING CAPITAL</div>',unsafe_allow_html=True)
    if st.session_state.done:
        ps=st.session_state.ps
        c1,c2,c3,c4=st.columns(4)
        with c1: st.markdown(f'<div class="metric-card-dark"><div class="metric-label">WC Health</div><div class="metric-value" style="color:{"#4ade80" if ps["score"]>=70 else "#f87171"}">{ps["score"]}</div><div style="font-size:0.78rem;color:#94a3b8;margin-top:0.3rem">{ps["health"]}</div><div class="mex" style="color:#64748b">100 - (CCC gap / benchmark x 50). 70+ Good, 45-69 At Risk, &lt;45 Critical.</div></div>',unsafe_allow_html=True)
        with c2: st.markdown(mcard("CCC",f'{ps["ccc"]}d',f'Bench: {ps["bench"]}d',"good" if ps["ccc"]<=ps["bench"] else "bad",f"DSO ({ps['dso']}d) + Inventory ({ps['inv']}d) - DPO ({ps['dpo']}d)","Standard financial formula. Every 1d reduction = Annual Revenue / 365 freed.","metric-card metric-card-blue"),unsafe_allow_html=True)
        with c3: st.markdown(mcard("AR > 90 Days",f'{ps["aging"]["90d"]}%',"Collection risk" if ps["aging"]["90d"]>=10 else "Low","bad" if ps["aging"]["90d"]>=10 else "good","% of invoices with DSO exceeding 90 days.","Target: <10%. High risk of write-off. Source: APQC Collections Benchmarks","metric-card metric-card-green" if ps["aging"]["90d"]<10 else "metric-card metric-card-red"),unsafe_allow_html=True)
        with c4: st.markdown(mcard("Deductions",fmtc(ps["deductions"],ccy),"Unvalidated","bad" if ps["deductions"]>1000 else "neutral","Sum of Deduction_USD. Taken without proper validation.","Expert Interview: early payment discounts taken outside contractual terms","metric-card metric-card-amber"),unsafe_allow_html=True)
        st.markdown("<br>",unsafe_allow_html=True)
        st.markdown('<div class="section-card"><div class="section-title">Cash Conversion Cycle</div><div class="mex" style="margin-top:-0.5rem;margin-bottom:0.75rem">CCC = DSO + Inventory Days - DPO. Every day reduced unlocks working capital = Annual Revenue / 365. Source: Standard financial metric; Expert Interview flagged working capital visibility as top CFO priority.</div>',unsafe_allow_html=True)
        cc1,cc2,cc3=st.columns(3)
        for col,(lb,v,co,fx,src) in zip([cc1,cc2,cc3],[("DSO",ps["dso"],"#dc2626","Reduce: faster invoicing, portal compliance bot, AI dunning","Days from invoice to payment. Bench: APQC O2C"),("Inventory Days",ps["inv"],"#f59e0b","Reduce: dynamic safety stock, FEFO automation, demand forecasting","Days inventory held before sale. Bench: Industry standard"),("DPO",ps["dpo"],"#16a34a","Increase: renegotiate supplier payment terms","Days to pay suppliers. Higher = better for your cash. Standard metric")]):
            with col: st.markdown(f'<div class="metric-card" style="text-align:center"><div class="metric-label">{lb}</div><div class="metric-value" style="color:{co}">{v}d</div><div style="font-size:0.78rem;color:#334155;margin-top:0.5rem">{fx}</div><div class="msrc">{src}</div></div>',unsafe_allow_html=True)
        st.markdown("</div>",unsafe_allow_html=True)
        st.markdown("<br>",unsafe_allow_html=True)
        al,ar=st.columns(2)
        with al:
            st.markdown('<div class="section-card"><div class="section-title">Receivables Aging</div><div class="mex" style="margin-top:-0.5rem;margin-bottom:0.75rem">Distribution of invoices by payment delay. Green = current. Red = 90+ days (write-off risk). Source: Your DSO data.</div>',unsafe_allow_html=True)
            for lb,v,co in [("Current (0-30d)",ps["aging"]["current"],"#16a34a"),("31-60 days",ps["aging"]["30d"],"#f59e0b"),("61-90 days",ps["aging"]["60d"],"#ea580c"),("90+ days",ps["aging"]["90d"],"#dc2626")]:
                st.markdown(f'<div style="margin-bottom:0.5rem"><div style="display:flex;justify-content:space-between;font-size:0.85rem;margin-bottom:3px"><span style="font-weight:500">{lb}</span><span style="font-family:JetBrains Mono,monospace;font-weight:600;color:{co}">{v}%</span></div><div class="progress-bar-bg"><div class="progress-bar-fill" style="width:{v}%;background:{co}"></div></div></div>',unsafe_allow_html=True)
            st.markdown("</div>",unsafe_allow_html=True)
        with ar:
            st.markdown('<div class="section-card"><div class="section-title">Upcoming Cash Position</div><div class="mex" style="margin-top:-0.5rem;margin-bottom:0.75rem">Forward-looking daily projection. Inflow = expected customer payments. Outflow = estimated operating costs. Select horizon below.</div>',unsafe_allow_html=True)
            cp=ps.get("cash_pos",[])
            if cp:
                hz=st.radio("Horizon",options=[7,14,21,30],horizontal=True,index=0,key="cp_hz")
                html='<table class="cp-table"><tr><th>Date</th><th>Expected Inflow</th><th>Expected Outflow</th><th>Net Flow</th></tr>'
                for row in cp[:hz]:
                    nc="cp-green" if row["Net"]>=0 else "cp-red"
                    html+=f'<tr><td style="font-weight:500;font-family:Inter,sans-serif">{row["Date"]}</td><td class="cp-green">{fmtc(row["Inflow"],ccy)}</td><td class="cp-red">{fmtc(row["Outflow"],ccy)}</td><td class="{nc}">{fmtc(row["Net"],ccy)}</td></tr>'
                html+='</table>'; st.markdown(html,unsafe_allow_html=True)
            st.markdown("</div>",unsafe_allow_html=True)
        # --- CollectIQ Dispute Resolution Engine ---
        if st.session_state.disputes and st.session_state.disputes["total"] > 0:
            dp = st.session_state.disputes
            st.markdown("<br>",unsafe_allow_html=True)
            st.markdown('<div class="section-card"><div class="section-title">CollectIQ — Dispute Resolution Engine</div><div class="mex" style="margin-top:-0.5rem;margin-bottom:0.75rem">AI-powered dispute workflow: auto-categorises disputes, pulls evidence from connected modules (ShipmentTracker, PriceGuard, BillingEngine), and recommends resolution. Source: CollectIQ (Normality Revenue Optimizer); Shib: "dispute handling on the receivables side is the primary O2C pain point."</div>',unsafe_allow_html=True)
            dp1,dp2,dp3,dp4=st.columns(4)
            with dp1: st.markdown(mcard("Active Disputes",f'{dp["total"]}',"From your data","neutral","Total orders flagged as Disputed = 1.","Source: Your uploaded O2C data","metric-card metric-card-red"),unsafe_allow_html=True)
            with dp2: st.markdown(mcard("Auto-Resolve Rate",f'{dp["auto_resolve_rate"]}%',"AI-resolved","good" if dp["auto_resolve_rate"]>=50 else "neutral","% disputes resolved without human intervention.","CollectIQ auto-pulls evidence and resolves clear-cut cases","metric-card metric-card-green" if dp["auto_resolve_rate"]>=50 else "metric-card metric-card-amber"),unsafe_allow_html=True)
            with dp3: st.markdown(mcard("Avg Resolution (After)",f'{dp["avg_days_after"]}d',"With CollectIQ","good","Estimated days to resolve with AI assistance.","Evidence auto-assembled from OrderIngest, ShipmentTracker, BillingEngine","metric-card metric-card-blue"),unsafe_allow_html=True)
            with dp4: st.markdown(mcard("Avg Resolution (Before)",f'{dp["avg_days_before"]}d',"Manual process","bad","Typical resolution time without automation.","Shib interview: 2-6 weeks for complex disputes","metric-card metric-card-red"),unsafe_allow_html=True)
            st.markdown("<br>",unsafe_allow_html=True)
            dpl,dpr=st.columns([1,2])
            with dpl:
                st.markdown('<div style="font-size:0.8rem;font-weight:600;color:#64748b;margin-bottom:0.5rem">BY CATEGORY</div>',unsafe_allow_html=True)
                for cat,cnt in dp["categories"].items():
                    pct=round(cnt/max(dp["total"],1)*100)
                    st.markdown(f'<div style="margin-bottom:0.5rem"><div style="display:flex;justify-content:space-between;font-size:0.82rem;margin-bottom:3px"><span style="font-weight:500">{cat}</span><span style="font-family:JetBrains Mono,monospace;font-weight:600">{cnt}</span></div><div class="progress-bar-bg"><div class="progress-bar-fill" style="width:{pct}%;background:#0369a1"></div></div></div>',unsafe_allow_html=True)
            with dpr:
                st.markdown('<div style="font-size:0.8rem;font-weight:600;color:#64748b;margin-bottom:0.5rem">DISPUTE QUEUE — AI RECOMMENDATIONS</div>',unsafe_allow_html=True)
                for item in dp["items"][:6]:
                    sv=item["Severity"]; sc="risk-high" if sv=="High" else "risk-med" if sv=="Medium" else "risk-low"
                    st_sc="risk-low" if item["Status"]=="Auto-Resolved" else "risk-med" if item["Status"]=="Pending Review" else "risk-high"
                    st.markdown(f'<div style="padding:0.5rem 0;border-bottom:1px solid #f1f5f9"><div style="display:flex;justify-content:space-between;align-items:center"><div><span style="font-weight:500;font-size:0.82rem">{item["Order_ID"]}</span> <span style="font-size:0.72rem;color:#94a3b8">· {item["Customer"]} · {fmtc(item["Invoice_Amount_USD"],ccy)}</span></div><div style="display:flex;gap:4px"><span class="risk-badge {sc}">{sv}</span><span class="risk-badge {st_sc}">{item["Status"]}</span></div></div><div style="font-size:0.75rem;color:#64748b;margin-top:3px"><span style="font-weight:500">{item["Dispute_Category"]}</span> · Est. {item["Est_Days"]}d</div><div style="font-size:0.75rem;color:#0369a1;margin-top:2px;background:#f0f9ff;padding:3px 6px;border-radius:4px">AI: {item["AI_Resolution"]}</div></div>',unsafe_allow_html=True)
            st.markdown("</div>",unsafe_allow_html=True)

# ==================== TAB 8: CASH APP & LTV ====================
with tabs[5]:
    if not st.session_state.done: st.info("Upload data and Run Full Analysis.")
    else:
        render_health_banner(show_modules=["Post-Sales & Financial Closure"])
        ltv_df = st.session_state.ltv
        ca = st.session_state.cash_app
        if ltv_df is not None and len(ltv_df) > 0:
            # AI recommendation
            avg_ltv = ltv_df["ltv_12m"].mean(); high_churn = (ltv_df["churn_risk"] == "High").sum(); strategic = (ltv_df["segment"] == "Strategic").sum(); avg_health = ltv_df["health_score"].mean()
            at_risk_rev = ltv_df[ltv_df["churn_risk"].isin(["High","Medium"])]["total_revenue"].sum()
            ltv_rec = f'Your customer portfolio has {len(ltv_df)} accounts with average 12-month LTV of {fmtc(avg_ltv,ccy)}.'
            if high_churn > 0: ltv_rec += f' {high_churn} customer{"s are" if high_churn>1 else " is"} flagged as high churn risk with {fmtc(at_risk_rev,ccy,True)} in revenue at stake — proactive outreach should be triggered immediately.'
            if ca and ca.get("match_rate",0) < 80: ltv_rec += f' Auto cash application match rate is {ca["match_rate"]}% — improving this through AI matching would accelerate cash recognition and reduce apparent AR.'
            bottom = ltv_df.tail(3)
            if len(bottom) > 0 and bottom["net_margin_pct"].mean() < 10: ltv_rec += f' Your bottom 3 customers average {bottom["net_margin_pct"].mean():.0f}% net margin after cost-to-serve — consider whether pricing or service level adjustments are needed.'
            st.markdown(f'<div style="background:linear-gradient(135deg,#faf5ff,#f3e8ff);border:2px solid #d8b4fe;border-radius:14px;padding:1.1rem 1.4rem;margin-bottom:1rem;box-shadow:0 2px 8px rgba(147,51,234,0.08)"><div style="font-size:0.7rem;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;color:#7c3aed;margin-bottom:0.4rem">🏦 AI RECOMMENDATION — CUSTOMER & CASH</div><div style="font-size:0.92rem;color:#3b0764;line-height:1.65">{ltv_rec}</div></div>',unsafe_allow_html=True)
            c1,c2,c3,c4=st.columns(4)
            with c1: st.markdown(mcard("Avg 12M LTV",fmtc(avg_ltv,ccy),"Per customer","neutral","Projected 12-month net margin per customer.","Revenue × margin - cost-to-serve (disputes, returns, deductions)","metric-card metric-card-blue"),unsafe_allow_html=True)
            with c2: st.markdown(mcard("High Churn Risk",f'{high_churn}',"Customers","bad" if high_churn>0 else "good","Customers with health score < 40.","Sime Darby CIDO: AI churn detection cited as priority","metric-card metric-card-red" if high_churn>0 else "metric-card metric-card-green"),unsafe_allow_html=True)
            with c3: st.markdown(mcard("Strategic Accounts",f'{strategic}',"High LTV + healthy","good","Top-quartile LTV and health ≥ 60.","LTV-driven pricing, credit, and service decisions (SPAN Module 5.5)","metric-card metric-card-green"),unsafe_allow_html=True)
            with c4: st.markdown(f'<div class="metric-card-dark"><div class="metric-label">Portfolio Health</div><div class="metric-value" style="color:{"#4ade80" if avg_health>=60 else "#f87171"}">{avg_health:.0f}</div><div style="font-size:0.78rem;color:#94a3b8;margin-top:0.3rem">{"Healthy" if avg_health>=60 else "At Risk"}</div><div class="mex" style="color:#64748b">Weighted: revenue 30% + frequency 20% + DSO 30% + disputes 20%</div></div>',unsafe_allow_html=True)
            st.markdown("<br>",unsafe_allow_html=True)
            st.markdown('<div class="section-card"><div class="section-title">Customer LTV Engine — Calculation Methodology</div><div class="mex" style="margin-top:-0.5rem;margin-bottom:0.75rem">Combines historical revenue, estimated gross margin, cost-to-serve, and behavioural signals into a single LTV score per customer. Source: Revenue Optimizer Module 5.5 (Normality); Sime Darby CIDO: "AI-driven customer LTV visibility was explicitly cited as a key strategic capability."</div>',unsafe_allow_html=True)
            fm1,fm2,fm3=st.columns(3)
            with fm1:
                st.markdown('<div style="background:#f0f9ff;border:1px solid #bae6fd;border-radius:8px;padding:1rem"><div style="font-size:0.78rem;font-weight:600;color:#0369a1;margin-bottom:0.5rem">REVENUE COMPONENT</div><div style="font-size:0.82rem;color:#334155;line-height:1.6">Monthly Revenue = Total Revenue ÷ Tenure Months<br>Projected 12M Revenue = Monthly Rev × 12<br>Est. Gross Margin = 35% of revenue<br><span style="font-size:0.72rem;color:#94a3b8">Source: FMCG industry avg margin</span></div></div>',unsafe_allow_html=True)
            with fm2:
                st.markdown('<div style="background:#fef3c7;border:1px solid #fcd34d;border-radius:8px;padding:1rem"><div style="font-size:0.78rem;font-weight:600;color:#92400e;margin-bottom:0.5rem">COST-TO-SERVE</div><div style="font-size:0.82rem;color:#334155;line-height:1.6">+ Deductions (from data)<br>+ Dispute cost: dispute_rate × 5%<br>+ Return cost: return_rate × 15%<br><span style="font-size:0.72rem;color:#94a3b8">Source: Normality SPAN; APQC</span></div></div>',unsafe_allow_html=True)
            with fm3:
                st.markdown('<div style="background:#dcfce7;border:1px solid #86efac;border-radius:8px;padding:1rem"><div style="font-size:0.78rem;font-weight:600;color:#166534;margin-bottom:0.5rem">LTV FORMULA</div><div style="font-size:0.82rem;color:#334155;line-height:1.6">LTV₁₂ = (Monthly Rev × 12 × 35%) − (Annual Cost-to-Serve)<br>Health = Rev 30% + Freq 20% + DSO 30% + Disputes 20%<br><span style="font-size:0.72rem;color:#94a3b8">Churn: Health &lt; 40 = High risk</span></div></div>',unsafe_allow_html=True)
            st.markdown("</div>",unsafe_allow_html=True)
            st.markdown("<br>",unsafe_allow_html=True)
            lt_l,lt_r=st.columns([3,2])
            with lt_l:
                st.markdown('<div class="section-card"><div class="section-title">Customer LTV Rankings</div><div class="mex" style="margin-top:-0.5rem;margin-bottom:0.5rem">Ranked by projected 12-month LTV. Revenue rank vs LTV rank reveals customers where revenue overstates true profitability.</div>',unsafe_allow_html=True)
                st.markdown('<div style="display:flex;justify-content:space-between;align-items:center;padding:6px 0;margin-bottom:6px;border-bottom:2px solid #e2e8f0"><div style="font-size:0.68rem;color:#94a3b8;font-weight:600">CUSTOMER · SEGMENT</div><div style="display:flex;align-items:center;gap:10px;font-size:0.68rem;color:#94a3b8;font-weight:600"><span>Rev Rank</span><span>LTV Rank</span><span style="width:80px;text-align:right">12M LTV ($)</span><span style="width:30px;text-align:center">Health</span><span style="width:50px;text-align:center">Churn</span></div></div>',unsafe_allow_html=True)
                # Compute revenue rank and LTV rank
                ranked = ltv_df.head(10).copy()
                ranked["rev_rank"] = ltv_df["total_revenue"].rank(ascending=False, method="min").astype(int)
                ranked["ltv_rank"] = ltv_df["ltv_12m"].rank(ascending=False, method="min").astype(int)
                ranked["misleading"] = (ranked["rev_rank"] - ranked["ltv_rank"]).abs() >= 3
                for idx,row in ranked.iterrows():
                    seg_co={"Strategic":"#166534","Growth":"#0369a1","At Risk":"#92400e","Monitor":"#64748b"}
                    seg_bg={"Strategic":"#dcfce7","Growth":"#e0f2fe","At Risk":"#fef3c7","Monitor":"#f1f5f9"}
                    churn_cls="risk-high" if row["churn_risk"]=="High" else "risk-med" if row["churn_risk"]=="Medium" else "risk-low"
                    hc=scolor(row["health_score"])
                    misleading_html = ""
                    if row["misleading"] or (row["segment"] in ["Monitor","At Risk"] and row["rev_rank"] <= 3):
                        misleading_html = f' <span style="font-size:0.62rem;padding:2px 7px;border-radius:8px;background:#fef2f2;color:#dc2626;font-weight:600;cursor:help" title="Revenue rank #{int(row["rev_rank"])} but LTV rank #{int(row["ltv_rank"])}. High cost-to-serve from disputes ({row["dispute_rate"]:.0f}%), deductions, and slow payment ({row["avg_dso"]:.0f}d DSO) erodes the apparent profitability. This customer appears valuable on top-line but is expensive to serve.">⚠ Revenue misleading</span>'
                    st.markdown(f'<div style="padding:0.6rem 0;border-bottom:1px solid #f1f5f9"><div style="display:flex;justify-content:space-between;align-items:center"><div><span style="font-weight:500;font-size:0.85rem">{row["Customer"]}</span> <span style="font-size:0.65rem;padding:2px 8px;border-radius:10px;background:{seg_bg.get(row["segment"],"#f1f5f9")};color:{seg_co.get(row["segment"],"#64748b")};font-weight:600">{row["segment"]}</span>{misleading_html}</div><div style="display:flex;align-items:center;gap:10px"><span style="font-size:0.65rem;color:#94a3b8">Rev #{int(row["rev_rank"])}</span><span style="font-size:0.65rem;color:{hc}">LTV #{int(row["ltv_rank"])}</span><span style="font-family:JetBrains Mono,monospace;font-size:0.85rem;font-weight:600">{fmtc(row["ltv_12m"],ccy)}</span><span style="font-family:JetBrains Mono,monospace;font-size:0.78rem;color:{hc}">{int(row["health_score"])}</span><span class="risk-badge {churn_cls}">{row["churn_risk"]}</span></div></div><div style="display:flex;gap:16px;font-size:0.72rem;color:#94a3b8;margin-top:3px"><span>Orders: {int(row["order_count"])}</span><span>DSO: {row["avg_dso"]:.0f}d</span><span>Net margin: {row["net_margin_pct"]}%</span><span>Rev: {fmtc(row["total_revenue"],ccy)}</span></div></div>',unsafe_allow_html=True)
                # Show expanded detail for misleading customers
                misleading_custs = ranked[(ranked["misleading"]) | ((ranked["segment"].isin(["Monitor","At Risk"])) & (ranked["rev_rank"] <= 3))]
                if len(misleading_custs) > 0:
                    for _,mc in misleading_custs.iterrows():
                        why_parts = []
                        if mc["avg_dso"] > 60: why_parts.append(f'DSO of {mc["avg_dso"]:.0f} days is well above the portfolio average — cash is trapped for longer')
                        if mc["dispute_rate"] > 5: why_parts.append(f'dispute rate of {mc["dispute_rate"]:.0f}% drives rework costs and delays collections')
                        if mc["net_margin_pct"] < 15: why_parts.append(f'net margin after cost-to-serve is only {mc["net_margin_pct"]}% despite strong top-line revenue')
                        if mc["deductions"] > 0: why_parts.append(f'{fmtc(mc["deductions"],ccy)} in deductions further erodes profitability')
                        why_text = ". ".join(why_parts) + "." if why_parts else "High cost-to-serve relative to revenue generated."
                        st.markdown(f'<div style="background:#fef2f2;border:1px solid #fecaca;border-radius:8px;padding:0.6rem 0.8rem;margin:0.4rem 0"><div style="font-size:0.72rem;font-weight:700;color:#991b1b">⚠ {mc["Customer"]} — Revenue Rank #{int(mc["rev_rank"])} vs LTV Rank #{int(mc["ltv_rank"])}</div><div style="font-size:0.78rem;color:#7f1d1d;line-height:1.5;margin-top:0.25rem">{why_text}</div><div style="font-size:0.72rem;color:#b91c1c;margin-top:0.25rem;font-weight:500">Recommendation: Review commercial terms, tighten credit limits, and consider whether this account justifies its service cost.</div></div>',unsafe_allow_html=True)
                st.markdown("</div>",unsafe_allow_html=True)
            with lt_r:
                st.markdown('<div class="section-card"><div class="section-title">Customer Segmentation</div><div class="mex" style="margin-top:-0.5rem;margin-bottom:0.75rem">Four-quadrant segmentation based on LTV and health score.</div>',unsafe_allow_html=True)
                seg_counts = ltv_df["segment"].value_counts()
                for seg in ["Strategic","Growth","At Risk","Monitor"]:
                    cnt = seg_counts.get(seg,0); pct = round(cnt/max(len(ltv_df),1)*100)
                    seg_co2={"Strategic":"#16a34a","Growth":"#0369a1","At Risk":"#f59e0b","Monitor":"#94a3b8"}
                    seg_desc={"Strategic":"High LTV + strong health — protect and grow","Growth":"Healthy engagement, room for revenue growth","At Risk":"High revenue but deteriorating health signals","Monitor":"Low LTV + low engagement — review cost-to-serve"}
                    st.markdown(f'<div style="margin-bottom:0.75rem"><div style="display:flex;justify-content:space-between;font-size:0.85rem;margin-bottom:3px"><span style="font-weight:500">{seg}</span><span style="font-family:JetBrains Mono,monospace;font-weight:600">{cnt} ({pct}%)</span></div><div class="progress-bar-bg"><div class="progress-bar-fill" style="width:{pct}%;background:{seg_co2.get(seg,"#94a3b8")}"></div></div><div style="font-size:0.7rem;color:#94a3b8;margin-top:2px">{seg_desc.get(seg,"")}</div></div>',unsafe_allow_html=True)
                st.markdown("</div>",unsafe_allow_html=True)
                st.markdown('<div class="section-card"><div class="section-title">Churn Risk Alerts</div><div class="mex" style="margin-top:-0.5rem;margin-bottom:0.75rem">Customers flagged for proactive outreach. Triggers: declining order frequency, extended DSO, rising disputes.</div>',unsafe_allow_html=True)
                at_risk = ltv_df[ltv_df["churn_risk"].isin(["High","Medium"])].head(5)
                for _,row in at_risk.iterrows():
                    churn_cls="risk-high" if row["churn_risk"]=="High" else "risk-med"
                    st.markdown(f'<div style="padding:0.5rem 0;border-bottom:1px solid #f1f5f9"><div style="display:flex;justify-content:space-between;align-items:center"><span style="font-weight:500;font-size:0.82rem">{row["Customer"]}</span><span class="risk-badge {churn_cls}">{row["churn_risk"]}</span></div><div style="font-size:0.72rem;color:#94a3b8;margin-top:2px">Health: {int(row["health_score"])} · DSO: {row["avg_dso"]:.0f}d · Disputes: {row["dispute_rate"]:.0f}%</div></div>',unsafe_allow_html=True)
                st.markdown("</div>",unsafe_allow_html=True)
            if ca and ca.get("total",0) > 0:
                st.markdown("<br>",unsafe_allow_html=True)
                st.markdown('<div class="section-card"><div class="section-title">CollectIQ — Auto Cash Application</div><div class="mex" style="margin-top:-0.5rem;margin-bottom:0.75rem">AI matches inbound payments to open invoices using three signals: amount matching (within 3% tolerance), identity matching (customer name/reference), and pattern matching (historical payment behaviour). Source: CollectIQ (Normality); Shib interview.</div>',unsafe_allow_html=True)
                ca1,ca2,ca3,ca4=st.columns(4)
                with ca1: st.markdown(mcard("Match Rate",f'{ca["match_rate"]}%',"Auto-matched","good" if ca["match_rate"]>=70 else "bad","% payments matched automatically (confidence ≥80).","CollectIQ NLP reads unstructured remittance advice","metric-card metric-card-green" if ca["match_rate"]>=70 else "metric-card metric-card-amber"),unsafe_allow_html=True)
                with ca2: st.markdown(mcard("Auto-Matched",f'{ca["auto_matched"]}',"of " + str(ca["total"]),"good","Payments matched without human intervention.","Amount + Identity + Pattern all confirmed","metric-card metric-card-blue"),unsafe_allow_html=True)
                with ca3: st.markdown(mcard("Review Required",f'{ca["manual_review"]}',"Partial match","neutral","Payments needing human review (confidence 45-79).","Ambiguous: some signals match, some don't","metric-card metric-card-amber"),unsafe_allow_html=True)
                with ca4: st.markdown(mcard("Unmatched",f'{ca["unmatched"]}',"Suspense","bad" if ca["unmatched"]>0 else "good","Payments with no matching signals.","Routes to manual allocation queue","metric-card metric-card-red" if ca["unmatched"]>0 else "metric-card metric-card-green"),unsafe_allow_html=True)
                st.markdown("<br>",unsafe_allow_html=True)
                for item in ca["items"][:10]:
                    conf_co = "#16a34a" if item["Confidence"] >= 80 else "#f59e0b" if item["Confidence"] >= 45 else "#dc2626"
                    st_cls = "risk-low" if item["Match_Status"] == "Auto-Matched" else "risk-med" if item["Match_Status"] == "Review Required" else "risk-high"
                    st.markdown(f'<div style="display:flex;justify-content:space-between;align-items:center;padding:0.5rem 0;border-bottom:1px solid #f1f5f9"><div><span style="font-weight:500;font-size:0.82rem">{item["Order_ID"]}</span> <span style="font-size:0.72rem;color:#94a3b8">· {item["Customer"]}</span><div style="font-size:0.72rem;color:#64748b;margin-top:2px">Invoice: {fmtc(item["Invoice_Amount_USD"],ccy)} → Remit: {fmtc(item["Remittance_Amount"],ccy)} · {item["Match_Method"]}</div></div><div style="display:flex;align-items:center;gap:8px"><span style="font-family:JetBrains Mono,monospace;font-size:0.82rem;color:{conf_co};font-weight:600">{item["Confidence"]}%</span><span class="risk-badge {st_cls}">{item["Match_Status"]}</span></div></div>',unsafe_allow_html=True)
                st.markdown("</div>",unsafe_allow_html=True)
