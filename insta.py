from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

#크롬 드라이버 자동으로 다운받는 webdriver-manager 설치. 
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By # find_element 함수 쉽게 쓰기 위함
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from collections import Counter
from itertools import chain
import pandas as pd
import time 
import re
# 크롬 드라이버 자동 업데이트
from webdriver_manager.chrome import ChromeDriverManager
#모듈 호출
from selenium.webdriver.common.keys import Keys


def create_driver():
    #브라우저 꺼짐 방지 
    chrome_options = Options()
    chrome_options.add_experimental_option("detach", True)

    # 불필요한 에러 메시지 없애기
    chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
    
    # 헤드리스 모드 활성화
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=chrome_options)
    return driver

def login_instagram(driver):
    #인스타로 이동
    driver.get('https://instagram.com')
    time.sleep(3)
    
    #인스타 로그인
    driver.implicitly_wait(10)
    login_id = driver.find_element(By.CSS_SELECTOR, 'input[name="username"]')
    login_id.send_keys('gudo.95') #아이디
    login_pwd = driver.find_element(By.CSS_SELECTOR, 'input[name="password"]')
    login_pwd.send_keys('gudo95') #비번
    driver.implicitly_wait(10)
    login_pwd.submit()
    time.sleep(2)
    login_id.send_keys(Keys.ENTER)
    #로그인 저장 나중에하기
    login_no_save = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, ".x78zum5.xdt5ytf.x1e56ztr .x1i10hfl.xjqpnuy"))
    )
    login_no_save.click()

#인스타 검색 결과 페이지
def insta_searching(word):
    url = 'https://www.instagram.com/explore/tags/' + word
    return url

# 옆 게시물로 이동
def move_next(driver):
    right = driver.find_element(By.CSS_SELECTOR, 'div._aaqg._aaqh')
    right.click()
    time.sleep(3)
    
# 데이터 수집하기
def get_content(driver):
    html = driver.page_source
    soup = BeautifulSoup(html, 'lxml')
    
    #본문 내용
    try:
        content = soup.select('div._a9zs')[0].text
    except:
        content = ""
        
    #해시태그
    tags = re.findall(r'#[^₩s#₩₩]+', content)
    
    data = tags
    return data

def collect_data(driver):
    # 데이터 쌓기
    results = []
    target = 10
    for i in range(target):
        try:
            data = get_content(driver)
            results.append(data)
            move_next(driver)
        except:
            time.sleep(2)
            move_next(driver)
            time.sleep(3)
    return results

# 가장 많이 나온 해시태그 10개와 그 개수를 반환하는 함수
def get_top_10_tags(tag_list):
    flattened_tags = [tag for sublist in tag_list for tag in sublist]
    tag_counts = Counter(flattened_tags)  # 각 해시태그의 빈도를 계산
    top_10_tags = tag_counts.most_common(10)  # 가장 많이 나온 해시태그 10개 추출
    return top_10_tags

@app.route('/insta/hashtags/<word>', methods=['GET'])
def get_hashtags(word):
    driver = create_driver()
    login_instagram(driver)
    #인스타 검색 결과 페이지
    search_url = insta_searching(word)
    driver.get(search_url)
    time.sleep(5)
    #첫번째 게시물 열기
    first = driver.find_elements(By.CSS_SELECTOR, 'div._aagw')[0]
    first.click()
    time.sleep(5)
    
    # 데이터 수집 및 해시태그 분석
    tag_data = collect_data(driver)
    # 상위 10개 해시태그 추출
    top_10_tags = get_top_10_tags(tag_data)
    
    # JSON 형식으로 반환
    hashtags_data = {
        "channel": "insta",
        "data": [{"id": tag, "value": count} for tag, count in top_10_tags]
    }
    driver.quit()
    return jsonify(hashtags_data)

if __name__ == '__main__':
    app.run(debug=True)