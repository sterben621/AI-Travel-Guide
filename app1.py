import json
import os
import sqlite3
import time
from flask_cors import CORS
from flask import Flask, jsonify, request, render_template, session, redirect, send_from_directory

app = Flask(__name__)
app.secret_key = "hualien_admin_secret_key"

# 1. 開啟 CORS 憑證支援 (修正 Session key 傳遞問題)
CORS(app, supports_credentials=True)

# 2. 設定 Session Cookie 屬性
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE'] = False  # 本地開發 (HTTP) 需設為 False

DB_NAME = "hualien_travel.db"
JSON_FILE = "花蓮.json"

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def init_db():
    """初始化資料庫並匯入 JSON 景點資料"""
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. 建立景點主表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS attractions (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            region TEXT,
            category TEXT,
            image_url TEXT,
            description TEXT,
            created_at TEXT
        )
    """)

    # 2. 建立收藏表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS favorites (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            attraction_id TEXT NOT NULL,
            collected_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, attraction_id),
            FOREIGN KEY (attraction_id) REFERENCES attractions(id) ON DELETE CASCADE
        )
    """)
    conn.commit()

    # 3. 自動讀取並匯入 JSON 資料
    if os.path.exists(JSON_FILE):
        try:
            with open(JSON_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)

            attractions_list = data.get("product", [])
            insert_data = []
            for item in attractions_list:
                insert_data.append((
                    item["id"],
                    item["title"],
                    item.get("region"),
                    item.get("category"),
                    item.get("image_url"),
                    item.get("description"),
                    item.get("created_at"),
                ))

            cursor.executemany("""
                INSERT OR IGNORE INTO attractions (id, title, region, category, image_url, description, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, insert_data)

            conn.commit()
            print(f"成功匯入 {len(insert_data)} 筆景點資料！")
        except Exception as e:
            print(f"JSON 匯入失敗: {e}")
    else:
        print(f"未找到 {JSON_FILE} 檔案，跳過初始資料匯入。")

    conn.close()

# 執行初始化
init_db()

# 獲取所有景點列表
@app.route("/api/attractions", methods=["GET"])
def get_all_attractions():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM attractions")
        rows = cursor.fetchall()
        attractions_list = [dict(row) for row in rows]
        return jsonify({"attractions": attractions_list}), 200
    except sqlite3.Error as e:
        return jsonify({"error": f"資料庫錯誤: {str(e)}"}), 500
    finally:
        conn.close()

# 新增景點 API
@app.route("/api/attractions", methods=["POST"])
def create_attraction():
    data = request.get_json()
    title = data.get("title")
    region = data.get("region")
    category = data.get("category", "自然風景")
    image_url = data.get("image_url", "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=500")
    description = data.get("description", "")

    if not title or not region:
        return jsonify({"error": "景點名稱與地區為必填欄位"}), 400

    attraction_id = f"HL-ATT-{int(time.time())}"
    created_at = time.strftime("%Y-%m-%d %H:%M:%S")

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO attractions (id, title, region, category, image_url, description, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (attraction_id, title, region, category, image_url, description, created_at))
        conn.commit()

        # 同步寫回 花蓮.json
        if os.path.exists(JSON_FILE):
            try:
                with open(JSON_FILE, "r+", encoding="utf-8") as f:
                    file_data = json.load(f)
                    file_data.setdefault("product", []).insert(0, {
                        "id": attraction_id,
                        "title": title,
                        "region": region,
                        "category": category,
                        "image_url": image_url,
                        "description": description,
                        "created_at": created_at
                    })
                    f.seek(0)
                    json.dump(file_data, f, ensure_ascii=False, indent=2)
                    f.truncate()
            except Exception as e:
                print(f"JSON 檔案同步更新失敗: {e}")

        return jsonify({
            "message": "成功新增景點",
            "attraction": {
                "id": attraction_id,
                "title": title,
                "region": region,
                "category": category,
                "image_url": image_url,
                "description": description,
                "created_at": created_at
            }
        }), 201
    except sqlite3.Error as e:
        conn.rollback()
        return jsonify({"error": f"資料庫寫入失敗: {str(e)}"}), 500
    finally:
        conn.close()

# 刪除景點 API (已補回同步刪除 JSON 邏輯)
@app.route("/api/attractions/<attraction_id>", methods=["DELETE"])
def delete_attraction(attraction_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # 1. 刪除資料庫紀錄
        cursor.execute("DELETE FROM attractions WHERE id = ?", (attraction_id,))
        conn.commit()

        # 2. 同步從 花蓮.json 移除
        if os.path.exists(JSON_FILE):
            try:
                with open(JSON_FILE, "r+", encoding="utf-8") as f:
                    file_data = json.load(f)
                    products = file_data.get("product", [])
                    file_data["product"] = [item for item in products if item.get("id") != attraction_id]
                    
                    f.seek(0)
                    json.dump(file_data, f, ensure_ascii=False, indent=2)
                    f.truncate()
            except Exception as e:
                print(f"JSON 檔案同步刪除失敗: {e}")

        return jsonify({"message": "已成功刪除景點"}), 200
    except sqlite3.Error as e:
        conn.rollback()
        return jsonify({"error": f"刪除失敗: {str(e)}"}), 500
    finally:
        conn.close()

# 收藏 API (POST)
@app.route("/api/favorite", methods=["POST"])
def toggle_favorite():
    data = request.get_json()
    user_id = data.get("user_id", "guest")
    attraction_id = data.get("attraction_id")

    if not attraction_id:
        return jsonify({"error": "缺少景點 ID"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT 1 FROM attractions WHERE id = ?", (attraction_id,))
        if not cursor.fetchone():
            return jsonify({"error": "找不到該景點資料"}), 404

        cursor.execute("SELECT 1 FROM favorites WHERE user_id = ? AND attraction_id = ?", (user_id, attraction_id))
        is_favorite = cursor.fetchone()

        if is_favorite:
            cursor.execute("DELETE FROM favorites WHERE user_id = ? AND attraction_id = ?", (user_id, attraction_id))
            status, message = "unfavorited", "已取消收藏"
        else:
            cursor.execute("INSERT INTO favorites (user_id, attraction_id) VALUES (?, ?)", (user_id, attraction_id))
            status, message = "favorited", "已加入收藏"

        conn.commit()
        return jsonify({"status": status, "message": message}), 200
    except sqlite3.Error as e:
        conn.rollback()
        return jsonify({"error": f"資料庫錯誤: {str(e)}"}), 500
    finally:
        conn.close()

# 刪除收藏 API (DELETE)
@app.route("/api/favorite", methods=["DELETE"])
def delete_favorite():
    data = request.get_json()
    user_id = data.get("user_id", "guest")
    attraction_id = data.get("attraction_id")

    if not attraction_id:
        return jsonify({"error": "缺少景點 ID"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT 1 FROM favorites WHERE user_id = ? AND attraction_id = ?", (user_id, attraction_id))
        if not cursor.fetchone():
            return jsonify({"error": "找不到該筆收藏紀錄，無法刪除"}), 404

        cursor.execute("DELETE FROM favorites WHERE user_id = ? AND attraction_id = ?", (user_id, attraction_id))
        conn.commit()
        return jsonify({"status": "unfavorited", "message": "已成功刪除該筆收藏"}), 200
    except sqlite3.Error as e:
        conn.rollback()
        return jsonify({"error": f"資料庫錯誤: {str(e)}"}), 500
    finally:
        conn.close()

# 取得收藏列表
@app.route("/api/favorites/<user_id>", methods=["GET"])
def get_favorites(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            SELECT a.*, f.collected_at 
            FROM favorites f
            JOIN attractions a ON f.attraction_id = a.id
            WHERE f.user_id = ?
            ORDER BY f.collected_at DESC
        ''', (user_id,))
        rows = cursor.fetchall()
        return jsonify({"user_id": user_id, "favorites": [dict(row) for row in rows]}), 200
    except sqlite3.Error as e:
        return jsonify({"error": f"資料庫錯誤: {str(e)}"}), 500
    finally:
        conn.close()

# 管理員相關功能
def create_admin_table():
    conn = sqlite3.connect("hualien_travel.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS admins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def insert_admin():
    if os.path.exists("admin.json"):
        with open("admin.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        admins = data.get("admins", [])

        conn = sqlite3.connect("hualien_travel.db")
        cursor = conn.cursor()
        for admin in admins:
            cursor.execute("""
                INSERT OR IGNORE INTO admins (username, password)
                VALUES (?, ?)
            """, (admin["username"], admin["password"]))
        conn.commit()
        conn.close()

def check_admin(username, password):
    conn = sqlite3.connect("hualien_travel.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM admins WHERE username=? AND password=?", (username, password))
    admin_user = cursor.fetchone()
    conn.close()
    return admin_user

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    print("========== 進入登入路由 ==========")
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        admin = check_admin(username, password)
        if admin:
            session["admin"] = username
            session.permanent = True  # 保持 session 狀態
            print(f"✅ 登入成功！已建立 Session：{dict(session)}")
            return redirect("/admin/dashboard")
        else:
            print("❌ 登入失敗！")
            return "帳號或密碼錯誤", 401

    return send_from_directory(os.path.join(app.root_path, "frontend"), "admin_login.html")

@app.route("/admin/dashboard")
def admin_dashboard():
    print("========== 進入後台首頁 ==========")
    print("目前 Session：", dict(session))

    if "admin" not in session:
        print("❌ 沒有 admin session，重定向至登入頁")
        return redirect("/admin/login")

    print(f"✅ 驗證成功，登入管理員：{session['admin']}")
    return send_from_directory(os.path.join(app.root_path, "frontend"), "manage.html")

@app.route("/frontend/<path:filename>")
def frontend_files(filename):
    return send_from_directory(os.path.join(app.root_path, "frontend"), filename)

@app.route("/")
def title_page():
    return send_from_directory(os.path.join(app.root_path, "frontend"), "welcome.html")

@app.route("/index")
def index():
    return send_from_directory(os.path.join(app.root_path, "frontend"), "index.html")

@app.route("/test2")
def test2():
    return send_from_directory(os.path.join(app.root_path, "frontend"), "test2.html")

@app.route("/favorite")
def favorite():
    return send_from_directory(os.path.join(app.root_path, "frontend"), "favorite.html")

if __name__ == '__main__':
    create_admin_table()
    insert_admin()
    app.run(debug=True, port=5000)