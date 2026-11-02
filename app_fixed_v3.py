import os
import sys
import sqlite3
import uuid
import traceback
from datetime import datetime, timedelta
from functools import wraps

from flask import Flask, render_template, request, url_for, redirect, session, jsonify, make_response

app = Flask(__name__)
app.secret_key = os.urandom(24)

# 데이터베이스 경로 설정
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database.db")

# 관리자 비밀 열쇠 (필요시 사용)
ADMIN_KEY = os.environ.get("ADMIN_KEY", "admin1234")

def get_db():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    return con

def init_db():
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            dummy1 TEXT,
            expiredate TEXT,
            query TEXT,
            이름 TEXT,
            주민등록번호 TEXT,
            집주소 TEXT,
            주민등록일자 TEXT,
            지역 TEXT,
            얼굴사진 TEXT
        )
    ''')
    cur.execute('''
        CREATE TABLE IF NOT EXISTS licenses (
            key TEXT PRIMARY KEY,
            expire_days INTEGER
        )
    ''')
    con.commit()
    con.close()

init_db()

# 라이선스 만료 여부 확인 함수
def is_license_expired(expiry_date_str):
    if not expiry_date_str or str(expiry_date_str).strip() in ["무제한", ""]:
        return False
    
    try:
        date_formats = [
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%d %H:%M',
            '%Y-%m-%d'
        ]
        
        expiry_date_str = str(expiry_date_str).strip()
        now = datetime.now()
        
        for fmt in date_formats:
            try:
                expiry_datetime = datetime.strptime(expiry_date_str, fmt)
                if expiry_datetime <= now:
                    return True
                else:
                    return False
            except ValueError:
                continue
        return False
    except Exception as e:
        print(f"라이선스 확인 오류: {e}")
        return False

# 만료된 사용자 자동 삭제 함수
def delete_expired_users():
    try:
        con = get_db()
        cur = con.cursor()
        cur.execute("SELECT id, expiredate, query FROM users WHERE expiredate IS NOT NULL AND expiredate != '' AND expiredate != '무제한'")
        rows = cur.fetchall()
        deleted_count = 0
        for row in rows:
            if is_license_expired(row['expiredate']):
                cur.execute("DELETE FROM users WHERE id = ?", (row['id'],))
                deleted_count += 1
        con.commit()
        con.close()
        if deleted_count > 0:
            print(f"[자동 정리] 총 {deleted_count}명의 만료된 사용자가 삭제되었습니다.")
    except Exception as e:
        print(f"[자동 정리] 오류 발생: {e}")

# ✅ / 와 /register 모두에서 GET 및 POST 요청을 처리하도록 통합
@app.route('/', methods=['GET', 'POST'])
@app.route('/register', methods=['GET', 'POST'])
def index_or_register():
    if request.method == 'POST':
        try:
            name = request.form.get('name')
            num = request.form.get('num')
            juso = request.form.get('juso')
            detail_juso = request.form.get('detail_juso', '')
            make = request.form.get('make')
            jiname = request.form.get('jiname')
            expiry_date = request.form.get('expiry_date', '').replace('T', ' ')
            if not expiry_date: 
                expiry_date = '무제한'
            
            license_key = request.form.get('license_key', '')
            if not license_key: 
                license_key = str(uuid.uuid4())[:12]

            # 사진 파일 업로드 처리
            photo = request.files.get('photo')
            imgurl = ""
            if photo and photo.filename:
                file_ext = os.path.splitext(photo.filename)[1]
                filename = f"{uuid.uuid4()}{file_ext}"
                
                os.makedirs(os.path.join(BASE_DIR, "static"), exist_ok=True)
                upload_path = os.path.join(BASE_DIR, "static", filename)
                photo.save(upload_path)
                imgurl = f"/static/{filename}"

            query = str(uuid.uuid4())[:8]
            full_juso = f"{juso} {detail_juso}".strip()

            con = get_db()
            cur = con.cursor()
            cur.execute('''
                INSERT INTO users (id, expiredate, query, 이름, 주민등록번호, 집주소, 주민등록일자, 지역, 얼굴사진)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (str(uuid.uuid4()), expiry_date, query, name, num, full_juso, make, jiname, imgurl))
            con.commit()
            con.close()

            return redirect(url_for('show_id', query=query))
        except Exception as e:
            traceback.print_exc()
            return f"등록 실패: {str(e)}", 500

    return render_template('register.html', admin_key=ADMIN_KEY)

@app.route('/api/users')
def get_users():
    try:
        con = get_db()
        cur = con.cursor()
        cur.execute("SELECT * FROM users")
        rows = cur.fetchall()
        data = [dict(row) for row in rows]
        con.close()
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/<query>')
def show_id(query):
    try:
        if query == 'favicon.ico': 
            return '', 204
            
        con = get_db()
        cur = con.cursor()
        cur.execute("SELECT * FROM users WHERE query = ?", (query,))
        row = cur.fetchone()
        
        if not row:
            con.close()
            return '''
                <html><head><meta charset="UTF-8"><title>오류</title></head>
                <body style="display:flex;justify-content:center;align-items:center;min-height:100vh;background:#f0f2f5;font-family:sans-serif;">
                <div style="background:white;padding:50px;border-radius:15px;text-align:center;box-shadow:0 4px 20px rgba(0,0,0,0.1);">
                <h1 style="color:#e74c3c;">❌ 삭제되었거나 존재하지 않는 신분증입니다.</h1>
                <p>링크를 다시 확인하시거나 관리자에게 문의해 주세요.</p>
                </div></body></html>
            ''', 404
        
        user = dict(row)
        exp = user.get('expiredate', '')
        
        if is_license_expired(exp):
            cur.execute("DELETE FROM users WHERE query = ?", (query,))
            con.commit()
            con.close()
            return '''
                <html><head><meta charset="UTF-8"><title>라이선스 만료</title></head>
                <body style="display:flex;justify-content:center;align-items:center;min-height:100vh;background:#f0f2f5;font-family:sans-serif;">
                <div style="background:white;padding:50px;border-radius:15px;text-align:center;box-shadow:0 4px 20px rgba(0,0,0,0.1);">
                <h1 style="color:#e74c3c;">⚠️ 라이선스 만료</h1>
                <p>이 신분증의 이용 기간이 만료되어 자동으로 삭제되었습니다.</p>
                <p>만료일자: <b>''' + str(exp) + '''</b></p>
                </div></body></html>
            ''', 403
        
        con.close()
        
        juso_val = user.get('집주소') or ''
        return render_template('sex.html', 
                             name=user.get('이름', ''), 
                             date=user.get('주민등록일자', ''), 
                             juso=juso_val, 
                             detail_juso=juso_val, 
                             imgurl=user.get('얼굴사진', ''), 
                             num=user.get('주민등록번호', ''), 
                             make=user.get('주민등록일자', ''), 
                             jiname=user.get('지역', ''), 
                             query=query)
    except Exception as e:
        traceback.print_exc()
        return f"조회 실패: {str(e)}", 500

@app.route('/qr_check/<query>')
def qr_check(query):
    try:
        con = get_db()
        cur = con.cursor()
        cur.execute("SELECT * FROM users WHERE query = ?", (query,))
        row = cur.fetchone()
        
        if not row:
            con.close()
            return "<h1>❌ 유효하지 않은 QR 코드입니다.</h1>", 404
        
        user = dict(row)
        exp = user.get('expiredate', '')
        
        if is_license_expired(exp):
            cur.execute("DELETE FROM users WHERE query = ?", (query,))
            con.commit()
            con.close()
            return "<h1>⚠️ 라이선스 만료로 삭제되었습니다.</h1>", 403
        
        con.close()
        
        jumin = user.get('주민등록번호') or '000000-0000000'
        birth_raw = jumin.split('-')[0] if '-' in jumin else jumin[:6]
        gender_code = jumin.split('-')[1][0] if '-' in jumin and len(jumin.split('-')[1]) > 0 else '1'
        year_prefix = "19" if gender_code in ['1', '2', '5', '6'] else "20"
        birth = f"{year_prefix}{birth_raw[0:2]}.{birth_raw[2:4]}.{birth_raw[4:6]}"

        return render_template('qr_check.html', 
                               name=user.get('이름', ''), 
                               birth=birth, 
                               jiname=user.get('지역', ''), 
                               imgurl=user.get('얼굴사진', ''))
    except Exception as e:
        traceback.print_exc()
        return f"검증 실패: {str(e)}", 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8890))
    app.run(host='0.0.0.0', port=port, debug=False)