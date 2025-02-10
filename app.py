from flask import Flask, render_template, request, redirect, url_for, session, flash,jsonify,g,make_response
import requests,time
from models import DBManager
from datetime import datetime, timedelta
import pytz
from werkzeug.utils import secure_filename
import json
# from dotenv import load_dotenv
import os
# .env 파일 로드
# load_dotenv()

app = Flask(__name__, static_folder="static") 
app.config['SECRET_KEY'] = 'your_secret_key'
db_manager = DBManager()

def time_ago(value):
    """ 상대적인 시간을 표시하는 함수 """
    now = datetime.now()  # 현재 서버 시간
    print(f"현재 시간: {now}, DB 시간: {value}")  # 디버깅용 출력

    diff = now - value
    if diff.total_seconds() < 60:
        return "방금 전"
    elif diff.total_seconds() < 3600:
        return f"{int(diff.total_seconds() // 60)}분 전"
    elif diff.total_seconds() < 86400:
        return f"{int(diff.total_seconds() // 3600)}시간 전"
    elif diff.total_seconds() < 604800:
        return f"{int(diff.total_seconds() // 86400)}일 전"
    elif diff.total_seconds() < 2592000:
        return f"{int(diff.total_seconds() // 604800)}주 전"
    elif diff.total_seconds() < 31536000:
        return f"{int(diff.total_seconds() // 2592000)}개월 전"
    else:
        return f"{int(diff.total_seconds() // 31536000)}년 전"
# Jinja에 필터 등록
app.jinja_env.filters['time_ago'] = time_ago


# 업로드된 파일을 저장할 폴더 설정
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    """확장자 검사"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


    
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'image' not in request.files:
        flash('파일을 선택해주세요.', 'danger')
        return redirect(request.url)

    file = request.files['image']
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)  # ✅ 안전한 파일명 변환
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)  # ✅ 안전한 경로에 저장
        flash('이미지 업로드 성공!', 'success')
        return redirect(url_for('index'))
    else:
        flash('허용되지 않은 파일 형식입니다.', 'danger')
        return redirect(request.url)
    
@app.before_request
def load_user():
    """ 모든 요청 전에 세션 정보를 context로 전달 """
    user_id = session.get("user_id")
    username = session.get("username")
    # 전역 변수처럼 사용 가능하게 설정
    g.user_id = user_id
    g.username = username

@app.route('/')
def index():
    user_id = session.get("user_id")
    username = session.get("username")
    return render_template('index.html', user_id=user_id, username=username)

    
# 회원가입
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        nickname = request.form['nickname']
        email = request.form['email']
        password = request.form['password']
        province = request.form.get('province')
        city = request.form.get('city')
        district = request.form.get('district', '')

        try:
            query = """
                INSERT INTO users (username, nickname, email, password, province, city, district) 
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            db_manager.execute_query(query, (username, nickname, email, password, province, city, district))

            flash('회원가입이 완료되었습니다. 로그인 해주세요.', 'success')

            return redirect(url_for('login'))  # ✅ 로그인 페이지로 이동
        except Exception as e:
            flash('회원가입 중 문제가 발생했습니다. 이메일이 중복되지 않았는지 확인해주세요.', 'danger')
            print(f"Error: {e}")

    return render_template('register.html')
# 로그인
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        query = "SELECT * FROM users WHERE email = %s"
        user = db_manager.fetch_one(query, (email,))

        if user and user['password'] == password:
            session['user_id'] = user['user_id']
            session['username'] = user['username']
            session['province'] = user['province']
            session['city'] = user['city']
            session['district'] = user['district']
            print(f"✅ 로그인 성공 - 세션 정보 저장: {session}")
            flash(f'{user["username"]}님, 환영합니다!', 'success')
            return redirect(url_for('index'))  

        else:
            flash('이메일 또는 비밀번호가 올바르지 않습니다.', 'danger')

    return render_template('login.html')

# 로그아웃
@app.route('/logout')
def logout():
    session.clear()
    flash('로그아웃되었습니다.', 'info')
    return redirect(url_for('login'))

#산책
@app.route('/walks', methods=['GET', 'POST'])
def walks():
    show_form = request.args.get('show_form', 'false').lower() == 'true'
    
    selected_province = request.args.get('province', session.get('province', ''))
    selected_city = request.args.get('city', session.get('city', ''))
    selected_district = request.args.get('district', session.get('district', ''))

    print(f"🔍 현재 필터 값: province={selected_province}, city={selected_city}, district={selected_district}")

    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        file = request.files.get('image')
        # 🔍 입력 값 로그 출력 (제대로 전달되는지 확인)
        print(f"📌 입력 확인: title={title}, description={description}")
        print("📌 글 작성 요청 감지됨!") 
        
        if 'user_id' not in session:
            flash("로그인이 필요합니다.", "danger")
            return redirect(url_for('login'))

        user_id = session['user_id']

        if not title or not description:
            flash('제목과 내용을 모두 입력하세요.', 'danger')
            return redirect(url_for('walks', show_form=True))

        # ✅ 게시글 작성 시 사용자의 지역 정보 자동 반영
        province = session.get('province', '') or '전체'
        city = session.get('city', '') or '전체'
        district = session.get('district', '') or '전체'

        location = f"{province} {city}".strip()
        if district:
            location += f" {district}"

        # ✅ 이미지 업로드 처리
        image_path = None
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            image_path = filename

        # ✅ 게시글 저장
        query = """
            INSERT INTO walks (title, description, location, province, city, district, user_id, image_path, created_at) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW())
        """
        db_manager.execute_query(query, (title, description,location, province, city, district, user_id, image_path))

        flash('산책 요청이 성공적으로 등록되었습니다.', 'success')
        return redirect(url_for('walks'))

    # ✅ 필터링 적용된 게시글 목록 가져오기
    query = """
    SELECT w.id, w.title, w.description, w.province, w.city, w.district, 
           COALESCE(w.image_path, '') AS image_path, w.created_at, 
           w.user_id AS author_id,
           COALESCE((SELECT COUNT(*) FROM likes WHERE post_id = w.id AND category = 'walks'), 0) AS like_count,
           COALESCE((SELECT COUNT(*) FROM comments WHERE post_id = w.id AND category = 'walks'), 0) AS comment_count
    FROM walks w
    WHERE (%s IN ('', '전체') OR w.province = %s)
        AND (%s IN ('', '전체') OR w.city = %s)
        AND (%s IN ('', '전체') OR w.district = %s)
    ORDER BY w.created_at DESC
    """
    posts = db_manager.fetch_all(query, (
        selected_province, selected_province,
        selected_city, selected_city,
        selected_district, selected_district
    ))
    
    return render_template(
        'walks.html',
        posts=posts,
        show_form=show_form,
        user_id=session.get('user_id'),
        selected_province=selected_province,
        selected_city=selected_city,
        selected_district=selected_district
    )
#산책글작성
@app.route('/walks/add', methods=['GET', 'POST'])
def add_walks():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        file = request.files.get('image')

        if 'user_id' not in session:
            flash("로그인이 필요합니다.", "danger")
            return redirect(url_for('login'))

        user_id = session['user_id']

        if not title or not description:
            flash('제목과 내용을 모두 입력하세요.', 'danger')
            return redirect(url_for('add_walks'))

        province = session.get('province', '') or '전체'
        city = session.get('city', '') or '전체'
        district = session.get('district', '') or '전체'

        location = f"{province} {city}".strip()
        if district:
            location += f" {district}"

        image_path = None
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            image_path = filename

        query = """
            INSERT INTO walks (title, description, location, province, city, district, user_id, image_path, created_at) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW())
        """
        db_manager.execute_query(query, (title, description, location, province, city, district, user_id, image_path))

        flash('산책 요청이 성공적으로 등록되었습니다.', 'success')
        return redirect(url_for('walks'))

    return render_template('add_walks.html')


# ✅ 산책 요청 상세보기 (user_id 포함)
@app.route('/walks/<int:post_id>', methods=['GET', 'POST'])
def walk_detail(post_id):
    user_id = session.get('user_id')
    username = session.get('username')
    # ✅ post_id 값이 Flask 라우트에서 제대로 들어오는지 확인
    print(f"📌 요청된 post_id: {post_id}")
    # ✅ 게시글 정보 가져오기 (작성자 닉네임 포함)
    post_query = """
        SELECT w.id, w.title, w.description, w.location, w.province, w.city, w.district, 
               w.image_path, w.created_at, 
               w.user_id AS author_id,
               COALESCE(u.nickname, '알 수 없음') AS author_nickname  
        FROM walks w
        LEFT JOIN users u ON w.user_id = u.user_id  
        WHERE w.id = %s
    """
    post = db_manager.fetch_one(post_query, (post_id,))
    print(f"📌 게시글 정보: {post}")  
    if not post:
        flash('해당 게시글을 찾을 수 없습니다.', 'danger')
        return redirect(url_for('walks'))

    # ✅ 댓글 목록 가져오기
    comments_query = """
        SELECT c.content, c.created_at, COALESCE(u.nickname, '알 수 없음') AS nickname
        FROM comments c 
        LEFT JOIN users u ON c.user_id = u.user_id  
        WHERE c.post_id = %s AND c.category = 'walks' 
        ORDER BY c.created_at ASC
    """
    comments = db_manager.fetch_all(comments_query, (post_id,))

    # ✅ 댓글 작성 기능
    if request.method == 'POST':
        if not user_id:
            flash('로그인 후 댓글을 작성할 수 있습니다.', 'danger')
            return redirect(url_for('login'))

        content = request.form.get('content', '').strip()
        if not content:
            flash('댓글을 입력하세요.', 'danger')
            return redirect(url_for('walk_detail', post_id=post_id))

        insert_query = "INSERT INTO comments (post_id, category, user_id, content) VALUES (%s, 'walks', %s, %s)"
        db_manager.execute_query(insert_query, (post_id, user_id, content))
        return redirect(url_for('walk_detail', post_id=post_id))

    return render_template(
        'walks.html',
        post=post,
        comments=comments,
        user_id=user_id,
        username=username
    )
    
#산책방 수정
@app.route('/walks/edit/<int:post_id>', methods=['GET', 'POST'])
def walk_edit(post_id):
    user_id = session.get('user_id')

    # ✅ 기존 게시글 가져오기 (작성자만 수정 가능)
    post_query = "SELECT * FROM walks WHERE id = %s AND user_id = %s"
    post = db_manager.fetch_one(post_query, (post_id, user_id))

    if not post:
        flash("수정할 게시글을 찾을 수 없거나 권한이 없습니다.", "danger")
        return redirect(url_for('walks'))

    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        file = request.files.get('image')

        # ✅ 이미지 변경 처리
        image_path = post['image_path']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            image_path = filename  # 새 이미지로 변경

        # ✅ 게시글 업데이트
        update_query = """
            UPDATE walks 
            SET title = %s, description = %s, image_path = %s
            WHERE id = %s AND user_id = %s
        """
        db_manager.execute_query(update_query, (title, description, image_path, post_id, user_id))

        flash("게시글이 성공적으로 수정되었습니다.", "success")
        return redirect(url_for('walk_detail', post_id=post_id))

    # ✅ 기존 게시글을 edit_walks.html로 렌더링
    return render_template('edit_walks.html', post=post)
# 돌봄 요청
@app.route('/petsitters', methods=['GET', 'POST'])
def petsitters():
    show_form = request.args.get('show_form', 'false').lower() == 'true'

    # ✅ 쿼리스트링(검색 필터)에서 값 가져오기 (없으면 세션값 사용)
    selected_province = request.args.get('province', session.get('province', ''))
    selected_city = request.args.get('city', session.get('city', ''))
    selected_district = request.args.get('district', session.get('district', ''))

    print(f"🔍 돌봄 요청 필터 값: province={selected_province}, city={selected_city}, district={selected_district}")

    if request.method == 'POST':
        if 'user_id' not in session:
            flash("로그인이 필요합니다.", "danger")
            return redirect(url_for('login'))

        user_id = session['user_id']
        title = request.form.get('title')
        description = request.form.get('description')
        file = request.files.get('image')

        if not title or not description:
            flash('제목과 내용을 모두 입력하세요.', 'danger')
            return redirect(url_for('petsitters', show_form=True))

        # ✅ 게시글 작성 시 사용자의 지역 정보 자동 반영
        province = session.get('province', '') or '전체'
        city = session.get('city', '') or '전체'
        district = session.get('district', '') or '전체'

        location = f"{province} {city}".strip()
        if district and district != '전체':
            location += f" {district}"

        print(f"📌 저장할 데이터: province={province}, city={city}, district={district}, location={location}")

        # ✅ 이미지 업로드 처리
        image_path = None
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            image_path = filename

        # ✅ 게시글 저장
        query = """
            INSERT INTO petsitters (title, description, location, province, city, district, user_id, image_path, created_at) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW())
        """
        db_manager.execute_query(query, (title, description, location, province, city, district, user_id, image_path))

        flash('돌봄 요청이 성공적으로 등록되었습니다.', 'success')
        return redirect(url_for('petsitters'))

    # ✅ 필터링 적용된 게시글 목록 가져오기
    query = """
    SELECT p.id, p.title, p.description, p.province, p.city, p.district, 
           COALESCE(p.image_path, '') AS image_path, p.created_at, 
           p.user_id AS author_id,
           COALESCE((SELECT COUNT(*) FROM likes WHERE post_id = p.id AND category = 'petsitters'), 0) AS like_count,
           COALESCE((SELECT COUNT(*) FROM comments WHERE post_id = p.id AND category = 'petsitters'), 0) AS comment_count
    FROM petsitters p
    WHERE (%s = '' OR p.province = %s)
      AND (%s = '' OR p.city = %s)
      AND (%s = '' OR p.district = %s)
    ORDER BY p.created_at DESC
    """
    posts = db_manager.fetch_all(query, (
        selected_province, selected_province,
        selected_city, selected_city,
        selected_district, selected_district
    ))

    print(f"📌 필터링된 돌봄 요청 게시글 개수: {len(posts)}")

    return render_template(
        'petsitters.html',
        posts=posts,
        show_form=show_form,
        user_id=session.get('user_id'),
        selected_province=selected_province,
        selected_city=selected_city,
        selected_district=selected_district
    )

@app.route('/petsitters/add', methods=['GET', 'POST'])
def add_petsitters():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        file = request.files.get('image')

        if 'user_id' not in session:
            flash("로그인이 필요합니다.", "danger")
            return redirect(url_for('login'))

        user_id = session['user_id']

        if not title or not description:
            flash('제목과 내용을 모두 입력하세요.', 'danger')
            return redirect(url_for('add_petsitters'))

        province = session.get('province', '') or '전체'
        city = session.get('city', '') or '전체'
        district = session.get('district', '') or '전체'

        location = f"{province} {city}".strip()
        if district:
            location += f" {district}"

        image_path = None
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            image_path = filename

        query = """
            INSERT INTO petsitters (title, description, location, province, city, district, user_id, image_path, created_at) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW())
        """
        db_manager.execute_query(query, (title, description, location, province, city, district, user_id, image_path))

        flash('돌봄 요청이 성공적으로 등록되었습니다.', 'success')
        return redirect(url_for('petsitters'))

    return render_template('add_petsitters.html')
# ✅ 돌봄 요청 상세보기 (도, 시, 동 정보 포함)
@app.route('/petsitters/<int:post_id>', methods=['GET', 'POST'])
def petsitter_detail(post_id):
    user_id = session.get('user_id')
    username = session.get('username')
    
    # ✅ 세션에서 사용자의 지역 정보 가져오기 (쿠키에서 변경)
    selected_province = session.get('province', '')  # 도
    selected_city = session.get('city', '')  # 시
    selected_district = session.get('district', '')  # 동


    post_query = """
    SELECT p.id, p.title, p.description, p.image_path, p.created_at, p.location,
           COALESCE(p.user_id, 0) AS author_id,  -- ✅ author_id 추가 (없으면 0)
           COALESCE((SELECT COUNT(*) FROM likes WHERE post_id = p.id AND category = 'petsitters'), 0) AS like_count
    FROM petsitters p
    WHERE p.id = %s
    """
    post = db_manager.fetch_one(post_query, (post_id,))

    if not post:
        flash('해당 게시글을 찾을 수 없습니다.', 'danger')
        return redirect(url_for('petsitters'))

    comments_query = """
        SELECT c.content, c.created_at, u.nickname 
        FROM comments c 
        JOIN users u ON c.user_id = u.user_id 
        WHERE c.post_id = %s AND c.category = 'petsitters' 
        ORDER BY c.created_at ASC
    """
    comments = db_manager.fetch_all(comments_query, (post_id,))

    if request.method == 'POST':
        if not user_id:
            flash('로그인 후 댓글을 작성할 수 있습니다.', 'danger')
            return redirect(url_for('login'))

        content = request.form['content']
        insert_query = "INSERT INTO comments (post_id, category, user_id, content) VALUES (%s, 'petsitters', %s, %s)"
        db_manager.execute_query(insert_query, (post_id, user_id, content))

        return redirect(url_for('petsitter_detail', post_id=post_id))

    return render_template(
        'petsitters.html',
        post=post,
        comments=comments,
        user_id=user_id,
        username=username,
        selected_province=selected_province,
        selected_city=selected_city,
        selected_district=selected_district
    )
#돌봄 수정
# 📌 돌봄 요청 수정 페이지
@app.route('/petsitters/edit/<int:post_id>', methods=['GET', 'POST'])
def petsitter_edit(post_id):
    user_id = session.get('user_id')
    if not user_id:
        flash("로그인이 필요합니다.", "danger")
        return redirect(url_for('login'))

    # ✅ 수정할 게시글 불러오기
    query = "SELECT * FROM petsitters WHERE id = %s AND user_id = %s"
    post = db_manager.fetch_one(query, (post_id, user_id))

    if not post:
        flash("게시글을 찾을 수 없거나 수정 권한이 없습니다.", "danger")
        return redirect(url_for('petsitters'))

    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        file = request.files.get('image')

        # ✅ 이미지 처리 (기존 이미지 유지)
        image_path = post['image_path']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            image_path = filename  # 새 이미지 업데이트

        # ✅ 게시글 업데이트
        update_query = """
            UPDATE petsitters
            SET title = %s, description = %s, image_path = %s, updated_at = NOW()
            WHERE id = %s AND user_id = %s
        """
        db_manager.execute_query(update_query, (title, description, image_path, post_id, user_id))

        flash("게시글이 수정되었습니다.", "success")
        return redirect(url_for('petsitters'))

    return render_template('edit_petsitter.html', post=post)
@app.route('/community', methods=['GET', 'POST'])
def community():
    show_form = request.args.get('show_form', 'false').lower() == 'true'

    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        file = request.files.get('image')
        user_id = session.get('user_id')

        if not user_id:
            flash('로그인 후 글을 작성할 수 있습니다.', 'danger')
            return redirect(url_for('login'))

        if not title or not content:
            flash('제목과 내용을 모두 입력하세요.', 'danger')
            return redirect(url_for('community', show_form=True))

        # ✅ 이미지 업로드 처리
        image_path = None  
        if file and allowed_file(file.filename):  
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            image_path = filename  

        # ✅ 게시글 저장 (이미지 포함)
        query = "INSERT INTO community_posts (title, content, user_id, image_path) VALUES (%s, %s, %s, %s)"
        db_manager.execute_query(query, (title, content, user_id, image_path))

        flash('소통방 글이 성공적으로 등록되었습니다.', 'success')
        return redirect(url_for('community'))

    # ✅ 목록 가져오기 (이미지 포함)
    query = """
        SELECT c.id, c.title, c.content, c.image_path, c.created_at, u.nickname,
               COALESCE((SELECT COUNT(*) FROM likes WHERE post_id = c.id AND category = 'community_posts'), 0) AS like_count,
               COALESCE((SELECT COUNT(*) FROM comments WHERE post_id = c.id AND category = 'community_posts'), 0) AS comment_count
        FROM community_posts c
        JOIN users u ON c.user_id = u.user_id
        ORDER BY c.created_at DESC
    """
    posts = db_manager.fetch_all(query)

    ####
     # ✅ 최근 3일간의 인기 게시글 가져오기 (좋아요 + 댓글 기준)
    three_days_ago = (datetime.now() - timedelta(days=3)).strftime('%Y-%m-%d %H:%M:%S')
    query_top_posts = """
    SELECT c.id, c.title, c.content, c.image_path, c.created_at, u.nickname,
           COALESCE((SELECT COUNT(*) FROM likes WHERE post_id = c.id AND category = 'community_posts' 
                     AND created_at >= NOW() - INTERVAL 3 DAY), 0) AS like_count,
           COALESCE((SELECT COUNT(*) FROM comments WHERE post_id = c.id AND category = 'community_posts' 
                     AND created_at >= NOW() - INTERVAL 3 DAY), 0) AS comment_count,
           (COALESCE((SELECT COUNT(*) FROM likes WHERE post_id = c.id AND category = 'community_posts' 
                     AND created_at >= NOW() - INTERVAL 3 DAY), 0) +
            COALESCE((SELECT COUNT(*) FROM comments WHERE post_id = c.id AND category = 'community_posts' 
                     AND created_at >= NOW() - INTERVAL 3 DAY), 0)) AS popularity_score
    FROM community_posts c
    JOIN users u ON c.user_id = u.user_id
    WHERE c.id IN (
        SELECT DISTINCT post_id FROM likes WHERE category = 'community_posts' AND created_at >= NOW() - INTERVAL 3 DAY
        UNION
        SELECT DISTINCT post_id FROM comments WHERE category = 'community_posts' AND created_at >= NOW() - INTERVAL 3 DAY
    )
    ORDER BY popularity_score DESC, c.created_at DESC
    LIMIT 10;
    """
    
    top_posts = db_manager.fetch_all(query_top_posts)
    return render_template('community.html', posts=posts, show_form=show_form, top_posts=top_posts)

@app.route('/community/edit/<int:post_id>', methods=['GET', 'POST'])
def edit_community(post_id):
    if 'user_id' not in session:
        flash("로그인이 필요합니다.", "danger")
        return redirect(url_for('login'))

    user_id = session['user_id']

    # ✅ 기존 게시글 데이터 가져오기
    query = "SELECT title, content, image_path FROM community_posts WHERE id = %s AND user_id = %s"
    post = db_manager.fetch_one(query, (post_id, user_id))

    if not post:
        flash("게시글을 찾을 수 없거나 수정 권한이 없습니다.", "danger")
        return redirect(url_for('community'))

    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        file = request.files.get('image')

        if not title or not content:
            flash("제목과 내용을 모두 입력하세요.", "danger")
            return redirect(url_for('edit_community', post_id=post_id))

        # ✅ 이미지 변경 처리 (새 이미지가 업로드되면 변경, 아니면 기존 이미지 유지)
        image_path = post['image_path']  # 기존 이미지 유지
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            image_path = filename  # 새 이미지로 교체

        # ✅ 기존 게시글 UPDATE
        query = """
            UPDATE community_posts
            SET title = %s, content = %s, image_path = %s, updated_at = NOW()
            WHERE id = %s AND user_id = %s
        """
        db_manager.execute_query(query, (title, content, image_path, post_id, user_id))

        flash("게시글이 성공적으로 수정되었습니다.", "success")
        return redirect(url_for('community'))

    return render_template('add_community.html', post=post)
@app.route('/community/add', methods=['GET', 'POST'])
def add_community():
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        file = request.files.get('image')

        if 'user_id' not in session:
            flash("로그인이 필요합니다.", "danger")
            return redirect(url_for('login'))

        user_id = session['user_id']

        if not title or not content:
            flash('제목과 내용을 모두 입력하세요.', 'danger')
            return redirect(url_for('add_community'))

        # ✅ 이미지 업로드 처리
        image_path = None
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            image_path = filename

        # ✅ 게시글 저장
        query = """
            INSERT INTO community_posts (title, content, user_id, image_path, created_at) 
            VALUES (%s, %s, %s, %s, NOW())
        """
        db_manager.execute_query(query, (title, content, user_id, image_path))

        flash('커뮤니티 글이 성공적으로 등록되었습니다.', 'success')
        return redirect(url_for('community'))

    return render_template('add_community.html')
# ✅ 소통방 상세보기 (댓글 기능)
@app.route('/community/<int:post_id>', methods=['GET', 'POST'])
def community_detail(post_id):
    user_id = session.get('user_id')
    username = session.get('username')

    # ✅ 게시글 정보 가져오기
    post_query = """
        SELECT c.id, c.title, c.content, c.created_at, 
               COALESCE(u.user_id, 0) AS author_id, 
               u.nickname
        FROM community_posts c
        JOIN users u ON c.user_id = u.user_id
        WHERE c.id = %s
    """
    post = db_manager.fetch_one(post_query, (post_id,))

    if not post:
        flash('해당 게시글을 찾을 수 없습니다.', 'danger')
        return redirect(url_for('community'))

    # 📌 댓글 목록 가져오기
    comments_query = """
        SELECT c.content, c.created_at, u.nickname 
        FROM comments c 
        JOIN users u ON c.user_id = u.user_id 
        WHERE c.post_id = %s AND c.category = 'community_posts' 
        ORDER BY c.created_at ASC
    """
    comments = db_manager.fetch_all(comments_query, (post_id,))

    # 📌 댓글 작성
    if request.method == 'POST':
        if not user_id:
            flash('로그인 후 댓글을 작성할 수 있습니다.', 'danger')
            return redirect(url_for('login'))

        content = request.form['content']
        insert_query = """
            INSERT INTO comments (post_id, category, user_id, content) 
            VALUES (%s, 'community_posts', %s, %s)
        """
        db_manager.execute_query(insert_query, (post_id, user_id, content))
        return redirect(url_for('community_detail', post_id=post_id))

    return render_template('community.html', post=post, comments=comments, user_id=user_id, username=username)

#########
# ✅ 게시글 목록 조회 (좋아요 & 댓글 수 포함)
def get_posts(category, table_name):
    query = f"""
        SELECT p.id, p.title, p.description, p.created_at, 
               COALESCE((SELECT COUNT(*) FROM likes WHERE post_id = p.id AND category = '{category}'), 0) AS like_count,
               COALESCE((SELECT COUNT(*) FROM comments WHERE post_id = p.id AND category = '{category}'), 0) AS comment_count
        FROM {table_name} p
        ORDER BY p.created_at DESC
    """
    posts = db_manager.fetch_all(query)
    return posts
# ✅ 상세 페이지 조회
def get_post_detail(category, table_name, post_id):
    query = f"""
        SELECT p.id, p.title, p.description, p.created_at,
               COALESCE((SELECT COUNT(*) FROM likes WHERE post_id = p.id AND category = '{category}'), 0) AS like_count
        FROM {table_name} p
        WHERE p.id = %s
    """
    post = db_manager.fetch_one(query, (post_id,))
    return post

# ✅ 댓글 조회
def get_comments(category, post_id):
    query = """
        SELECT c.content, c.created_at, u.nickname 
        FROM comments c 
        JOIN users u ON c.user_id = u.user_id 
        WHERE c.post_id = %s AND c.category = %s 
        ORDER BY c.created_at ASC
    """
    comments = db_manager.fetch_all(query, (post_id, category))
    return comments

# ✅ 게시글 목록 및 상세보기 처리/
@app.route('/<category>', methods=['GET', 'POST'])
def posts(category):
    valid_categories = {
        "walks": ("산책 요청", "walks", "walks.html"),
        "petsitters": ("돌봄 요청", "petsitters", "petsitters.html"),
        "community": ("소통방", "community_posts", "community.html")
    }

    if category not in valid_categories:
        return "잘못된 카테고리", 404

    category_name, table_name, template_file = valid_categories[category]
    post_id = request.args.get('post_id')

    # ✅ 로그인된 사용자 정보 가져오기
    user_id = session.get("user_id")
    username = session.get("username")

    if post_id:  # 상세 페이지
        post = get_post_detail(category, table_name, post_id)
        comments = get_comments(category, post_id)
        return render_template(
            template_file,
            post=post, comments=comments, 
            user_id=user_id, username=username, category=category
        )

    # 목록 페이지
    posts = get_posts(category, table_name)
    return render_template(
        template_file,
        posts=posts,
        user_id=user_id, username=username, category=category
    )
@app.route("/like/<category>/<int:post_id>", methods=["POST"])
def like_post(category, post_id):
    """ 좋아요 처리 API """
    if "user_id" not in session:
        return jsonify({"success": False, "error": "로그인이 필요합니다."}), 401

    user_id = session["user_id"]

    query = "SELECT * FROM likes WHERE post_id = %s AND category = %s AND user_id = %s"
    
    db_manager = DBManager()
    
    retry_count = 3  # 재시도 횟수
    for attempt in range(retry_count):
        try:
            existing_like = db_manager.fetch_one(query, (post_id, category, user_id))

            if existing_like:
                delete_query = "DELETE FROM likes WHERE post_id = %s AND category = %s AND user_id = %s"
                db_manager.execute_query(delete_query, (post_id, category, user_id))
                return jsonify({"success": True, "liked": False})
            else:
                insert_query = "INSERT INTO likes (post_id, category, user_id) VALUES (%s, %s, %s)"
                db_manager.execute_query(insert_query, (post_id, category, user_id))
                return jsonify({"success": True, "liked": True})

        except mysql.connector.Error as error:
            print(f"🚨 좋아요 처리 중 오류 발생: {error}")
            if "Lost connection" in str(error) or "MySQL server has gone away" in str(error):
                print("🔄 MySQL 재연결 시도 중...")
                time.sleep(1)  # 1초 대기 후 재시도
                db_manager = DBManager()  # 새 DBManager 인스턴스 생성
            else:
                return jsonify({"success": False, "error": "서버 오류 발생"}), 500

    return jsonify({"success": False, "error": "MySQL 재연결 실패"}), 500
################채팅

# ✅ 채팅방 생성 또는 기존 채팅방 가져오기
@app.route('/start_chat/<int:post_id>/<int:author_id>/<category>', methods=['POST'])
def start_chat(post_id, author_id, category):
    sender_id = session.get('user_id')
    if not sender_id:
        return jsonify({"success": False, "error": "로그인이 필요합니다."}), 403

    if sender_id == author_id:
        return jsonify({"success": False, "error": "자신과는 채팅할 수 없습니다."}), 400

    # 📌 post_id가 유효한지 확인 (데이터베이스 조회)
    valid_post = None
    if category == "walks":
        valid_post = db_manager.fetch_one("SELECT id FROM walks WHERE id = %s", (post_id,))
    elif category == "petsitters":
        valid_post = db_manager.fetch_one("SELECT id FROM petsitters WHERE id = %s", (post_id,))
    elif category == "community_posts":
        valid_post = db_manager.fetch_one("SELECT id FROM community_posts WHERE id = %s", (post_id,))

    if not valid_post:
        return jsonify({"success": False, "error": "해당 게시글이 존재하지 않습니다."}), 400

    # 📌 기존 채팅방 있는지 확인
    query = """
        SELECT id FROM chat_rooms 
        WHERE (user1_id = %s AND user2_id = %s AND post_id = %s AND category = %s) 
           OR (user1_id = %s AND user2_id = %s AND post_id = %s AND category = %s)
    """
    existing_chat = db_manager.fetch_one(query, (sender_id, author_id, post_id, category,
                                                 author_id, sender_id, post_id, category))

    if existing_chat:
        chat_id = existing_chat['id']
    else:
        # 📌 채팅방 생성
        insert_query = "INSERT INTO chat_rooms (user1_id, user2_id, post_id, category, created_at) VALUES (%s, %s, %s, %s, NOW())"
        db_manager.execute_query(insert_query, (sender_id, author_id, post_id, category))
        chat_id = db_manager.fetch_one("SELECT LAST_INSERT_ID() AS chat_id")['chat_id']

    return jsonify({"success": True, "chat_url": url_for('chat_room', chat_id=chat_id)})
# ✅ 채팅 목록 + 관련 게시글 정보
@app.route('/chat', methods=['GET'])
def chat():
    user_id = session.get('user_id')
    if not user_id:
        flash("로그인이 필요합니다.", "danger")
        return redirect(url_for('login'))

    # ✅ 기존 중복 제거된 채팅방 목록 가져오기
    query = """
        SELECT MIN(c.id) AS chat_id, 
               CASE 
                   WHEN c.user1_id = %s THEN u2.username
                   ELSE u1.username
               END AS chat_partner,
               c.category,
               c.post_id,
               COALESCE(w.title, cp.title, p.title, '게시글 없음') AS post_title
        FROM chat_rooms c
        JOIN users u1 ON c.user1_id = u1.user_id
        JOIN users u2 ON c.user2_id = u2.user_id
        LEFT JOIN walks w ON c.category = 'walks' AND c.post_id = w.id
        LEFT JOIN community_posts cp ON c.category = 'community_posts' AND c.post_id = cp.id
        LEFT JOIN petsitters p ON c.category = 'petsitters' AND c.post_id = p.id
        WHERE c.user1_id = %s OR c.user2_id = %s
        GROUP BY c.user1_id, c.user2_id, c.post_id, c.category, u1.username, u2.username, w.title, cp.title, p.title;
    """
    chat_rooms = db_manager.fetch_all(query, (user_id, user_id, user_id))

    # ✅ 첫 번째 채팅방 ID 설정 (없으면 None)
    first_chat_id = chat_rooms[0]['chat_id'] if chat_rooms else None

    # ✅ 첫 번째 채팅방 메시지 가져오기 (채팅방이 존재할 때만)
    messages = []
    if first_chat_id:
        messages_query = """
            SELECT sender_id, message, created_at
            FROM messages
            WHERE chat_id = %s
            ORDER BY created_at ASC
        """
        messages = db_manager.fetch_all(messages_query, (first_chat_id,))

    return render_template('chat.html', messages=messages, chat_rooms=chat_rooms, chat_id=first_chat_id, user_id=user_id)

# ✅ 특정 채팅방의 메시지 표시
@app.route('/chat_room/<int:chat_id>', methods=['GET', 'POST'])
def chat_room(chat_id):
    user_id = session.get('user_id')
    if not user_id:
        flash("로그인이 필요합니다.", "danger")
        return redirect(url_for('login'))

    # ✅ 현재 채팅방 메시지 불러오기
    messages_query = """
        SELECT m.sender_id, m.message, m.created_at, u.username AS sender_name
        FROM messages m
        JOIN users u ON m.sender_id = u.user_id
        WHERE m.chat_id = %s
        ORDER BY m.created_at ASC
    """
    messages = db_manager.fetch_all(messages_query, (chat_id,))

    # ✅ 채팅 목록도 함께 불러오기
    chat_list_query = """
        SELECT c.id AS chat_id, 
               CASE 
                   WHEN c.user1_id = %s THEN u2.username
                   ELSE u1.username
               END AS chat_partner,
               c.category,
               c.post_id,
               COALESCE(w.title, cp.title, p.title, '게시글 없음') AS post_title,
               COALESCE(w.user_id, cp.user_id, p.user_id, 0) AS author_id  -- ✅ 게시글 작성자 ID 가져오기
        FROM chat_rooms c
        JOIN users u1 ON c.user1_id = u1.user_id
        JOIN users u2 ON c.user2_id = u2.user_id
        LEFT JOIN walks w ON c.category = 'walks' AND c.post_id = w.id
        LEFT JOIN community_posts cp ON c.category = 'community_posts' AND c.post_id = cp.id
        LEFT JOIN petsitters p ON c.category = 'petsitters' AND c.post_id = p.id
        WHERE c.user1_id = %s OR c.user2_id = %s
    """
    chat_rooms = db_manager.fetch_all(chat_list_query, (user_id, user_id, user_id))

    # ✅ 현재 채팅방에 대한 게시글 정보 가져오기
    post_info = None
    if chat_rooms:
        for chat in chat_rooms:
            if chat['chat_id'] == chat_id:
                post_info = {
                    "post_id": chat['post_id'] if chat['post_id'] is not None else 0,
                    "post_title": chat['post_title'] if chat['post_title'] is not None else "게시글 없음",
                    "category": chat['category'] if chat['category'] is not None else "unknown",
                    "author_id": chat['author_id'] if chat['author_id'] is not None else 0  # ✅ 게시글 작성자 ID 추가
                }
                break

    return render_template('chat.html', messages=messages, chat_rooms=chat_rooms, chat_id=chat_id, user_id=user_id, post_info=post_info)

# ✅ 메시지 전송 API
@app.route('/send_message/<int:chat_id>', methods=['POST'])
def send_message(chat_id):
    sender_id = session.get('user_id')
    if not sender_id:
        flash("로그인이 필요합니다.", "danger")
        return redirect(url_for('login'))

    message = request.form['message']
    query = "INSERT INTO messages (chat_id, sender_id, message, created_at) VALUES (%s, %s, %s, NOW())"
    db_manager.execute_query(query, (chat_id, sender_id, message))

    return redirect(url_for('chat_room', chat_id=chat_id))

@app.route('/delete_post/<category>/<int:post_id>', methods=['POST'])
def delete_post(category, post_id):
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'message': '로그인이 필요합니다.'}), 403

    # 카테고리별 테이블 이름 매핑
    category_table_map = {
        'walks': 'walks',
        'petsitters': 'petsitters',
        'community_posts': 'community_posts'
    }

    # 존재하는 카테고리인지 확인
    if category not in category_table_map:
        return jsonify({'success': False, 'message': '잘못된 카테고리입니다.'}), 400

    table_name = category_table_map[category]

    # 게시글 작성자 확인
    query = f"SELECT user_id FROM {table_name} WHERE id = %s"
    post = db_manager.fetch_one(query, (post_id,))

    if not post:
        return jsonify({'success': False, 'message': '게시글이 존재하지 않습니다.'}), 404

    if post['user_id'] != user_id:
        return jsonify({'success': False, 'message': '삭제 권한이 없습니다.'}), 403

    # 게시글 삭제
    delete_query = f"DELETE FROM {table_name} WHERE id = %s"
    db_manager.execute_query(delete_query, (post_id,))

    return jsonify({'success': True, 'message': '게시글이 삭제되었습니다.'})

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")