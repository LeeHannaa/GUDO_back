from flask import Flask, jsonify, request
from datetime import datetime
from pytrends.request import TrendReq
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Google Trends API 연결
pytrends = TrendReq(hl='ko', tz=540)

@app.route('/trends/<keywords>/<start_date>/<end_date>', methods=['GET'])
def get_trends(keywords, start_date, end_date):
    # 쿼리 파라미터로 받은 키워드와 기간 정보
    if not keywords:
        return jsonify({'error': '키워드를 입력하세요.'}), 400
    
    try:
        datetime.strptime(start_date, '%Y-%m-%d')
        datetime.strptime(end_date, '%Y-%m-%d')
    except ValueError:
        return jsonify({'error': '날짜 형식이 올바르지 않습니다. 형식: YYYY-MM-DD'}), 400

    kw_list = keywords.split(',')  # 콤마로 구분된 키워드를 리스트로 변환
    timeframe = f'{start_date} {end_date}'
    pytrends.build_payload(kw_list, cat=0, timeframe=timeframe, geo='KR', gprop='')

    # 트렌드 데이터를 가져옴
    data = pytrends.interest_over_time()

    if data.empty:
        return jsonify({'error': '데이터가 없습니다.'}), 404

    averages = {}
    for keyword in kw_list:
        if keyword in data.columns:
            averages[keyword] = {
                "count": round(data[keyword].mean()),
                "ratio": round((data[keyword] / data[kw_list].sum(axis=1) * 100).mean())  # 각 키워드의 비율 계산
            }

    # 결과를 JSON으로 변환하여 반환
    result = [{"word": keyword, "count": averages[keyword]["count"], "ratio": averages[keyword]["ratio"]} for keyword in kw_list]
    
    return jsonify(result)



# 오늘+어제 급상승 검색어 상위 20개까지 반환 south_korea, canada, united_states
@app.route('/trends/top20/<country>', methods=['GET'])
def get_top20_trends(country):
    try:
        data = pytrends.trending_searches(pn=country)
        if data.empty:
            return jsonify({'error': '데이터가 없습니다.'}), 404

        result = [{"id": index + 1, "word": value[0]} for index, value in data.iterrows()]
        return jsonify(result)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
