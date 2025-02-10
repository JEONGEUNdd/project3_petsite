CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    nickname VARCHAR(50),
    email VARCHAR(100) UNIQUE NOT NULL,
    PASSWORD VARCHAR(255) NOT NULL
);

CREATE TABLE pets (
    pet_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    pet_name VARCHAR(50) NOT NULL,
    species VARCHAR(50),
    age INT,
    personality VARCHAR(255)
);

CREATE TABLE walks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE petsitters (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE community_posts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    user_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE comments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    post_id INT NOT NULL,
    category ENUM('walks', 'petsitters', 'community_posts') NOT NULL,
    user_id INT NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

CREATE TABLE likes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    post_id INT NOT NULL,
    category ENUM('walks', 'petsitters', 'community_posts') NOT NULL,
    user_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (post_id, category, user_id)  -- 중복 좋아요 방지
);
SELECT * FROM likes WHERE category = 'community_posts';
UPDATE likes SET category = 'community_posts' WHERE category = 'community';

ALTER TABLE walks ADD COLUMN user_id INT NOT NULL;
ALTER TABLE petsitters ADD COLUMN user_id INT NOT NULL;
ALTER TABLE walks ADD COLUMN image_path VARCHAR(255);
ALTER TABLE petsitters ADD COLUMN image_path VARCHAR(255);
ALTER TABLE community_posts ADD COLUMN image_path VARCHAR(255);
SELECT * FROM petsitters;
SELECT id, title, description, image_url FROM petsitters;

CREATE TABLE chat_rooms (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user1_id INT NOT NULL,
    user2_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE messages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    chat_id INT NOT NULL,
    sender_id INT NOT NULL,
    message TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

ALTER TABLE walks ADD COLUMN location VARCHAR(255);
ALTER TABLE petsitters ADD COLUMN location VARCHAR(255);

#기존 데이터 중 location이 NULL이면 기본값 설정
UPDATE walks SET location = '서울' WHERE location IS NULL OR location = '';
UPDATE petsitters SET location = '서울' WHERE location IS NULL OR location = '';

# location을 필수 입력값으로 설정
ALTER TABLE walks MODIFY COLUMN location VARCHAR(255) NOT NULL;
ALTER TABLE petsitters MODIFY COLUMN location VARCHAR(255) NOT NULL;

#######################
ALTER TABLE walks DROP COLUMN location;
ALTER TABLE petsitters DROP COLUMN location;

-- ������ 새 컬럼 추가 (도, 시, 동)
ALTER TABLE walks ADD COLUMN province VARCHAR(50) NOT NULL;
ALTER TABLE walks ADD COLUMN city VARCHAR(50) NOT NULL;
ALTER TABLE walks ADD COLUMN district VARCHAR(50) DEFAULT NULL;

ALTER TABLE petsitters ADD COLUMN province VARCHAR(50) NOT NULL;
ALTER TABLE petsitters ADD COLUMN city VARCHAR(50) NOT NULL;
ALTER TABLE petsitters ADD COLUMN district VARCHAR(50) DEFAULT NULL;

-- ������ 기존 데이터 중 location이 NULL이면 기본값 설정 (서울특별시, 종로구)
UPDATE walks SET province = '서울특별시', city = '종로구' WHERE province IS NULL OR province = '';
UPDATE petsitters SET province = '서울특별시', city = '종로구' WHERE province IS NULL OR province = '';

-- ������ 필수 입력값 설정
ALTER TABLE walks MODIFY COLUMN province VARCHAR(50) NOT NULL;
ALTER TABLE walks MODIFY COLUMN city VARCHAR(50) NOT NULL;
ALTER TABLE petsitters MODIFY COLUMN province VARCHAR(50) NOT NULL;
ALTER TABLE petsitters MODIFY COLUMN city VARCHAR(50) NOT NULL;

#회원가입 시 도, 시, 동 정보를 저장
ALTER TABLE users 
ADD COLUMN province VARCHAR(50) NOT NULL,
ADD COLUMN city VARCHAR(50) NOT NULL,
ADD COLUMN district VARCHAR(50) DEFAULT NULL;  

ALTER TABLE walks ADD COLUMN location VARCHAR(255) NOT NULL;
ALTER TABLE petsitters ADD COLUMN location VARCHAR(255) NOT NULL;
SELECT * FROM chat_rooms WHERE (user1_id = 7 AND user2_id = 1) OR (user1_id = 1 AND user2_id = 7);

#중복 채팅방 제거
DELETE c1 FROM chat_rooms c1
JOIN chat_rooms c2 
ON c1.user1_id = c2.user1_id 
AND c1.user2_id = c2.user2_id
AND c1.post_id = c2.post_id
AND c1.category = c2.category
AND c1.id > c2.id;

ALTER TABLE chat_rooms AUTO_INCREMENT = 1;

SELECT user1_id, user2_id, post_id, category, COUNT(*) AS duplicate_count
FROM chat_rooms
GROUP BY user1_id, user2_id, post_id, category
HAVING COUNT(*) > 1;

SELECT MIN(id) AS id, user1_id, user2_id, post_id, category
FROM chat_rooms
GROUP BY user1_id, user2_id, post_id, category;

UPDATE users SET district = '' WHERE district IS NULL;
UPDATE walks SET district = '' WHERE district IS NULL;
UPDATE petsitters SET district = '' WHERE district IS NULL;

UPDATE walks 
SET district = '전체' 
WHERE district IS NULL OR district = '';

########
-- ������ 반려동물과 사용자 연결
ALTER TABLE pets 
ADD CONSTRAINT fk_pets_user 
FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE;

-- ������ 산책 요청과 사용자 연결
ALTER TABLE walks 
ADD CONSTRAINT fk_walks_user 
FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE;

-- ������ 돌봄 요청과 사용자 연결
ALTER TABLE petsitters 
ADD CONSTRAINT fk_petsitters_user 
FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE;

-- ������ 커뮤니티 게시글과 사용자 연결
ALTER TABLE community_posts 
ADD CONSTRAINT fk_community_posts_user 
FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE;

-- ������ 댓글과 게시글 및 사용자 연결
ALTER TABLE comments 
ADD CONSTRAINT fk_comments_user 
FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE;
##3

-- ������ 좋아요와 게시글 및 사용자 연결
ALTER TABLE likes 
ADD CONSTRAINT fk_likes_user 
FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE;


-- ������ 채팅방과 사용자 연결
ALTER TABLE chat_rooms 
ADD CONSTRAINT fk_chat_rooms_user1 
FOREIGN KEY (user1_id) REFERENCES users(user_id) ON DELETE CASCADE;

ALTER TABLE chat_rooms 
ADD CONSTRAINT fk_chat_rooms_user2 
FOREIGN KEY (user2_id) REFERENCES users(user_id) ON DELETE CASCADE;

-- ������ 메시지와 채팅방 및 사용자 연결
SELECT COUNT(*) 
FROM messages 
WHERE chat_id IS NULL;



SELECT DISTINCT chat_id 
FROM messages 
WHERE chat_id NOT IN (SELECT id FROM chat_rooms);

DELETE FROM messages 
WHERE chat_id NOT IN (SELECT id FROM chat_rooms);

UPDATE messages 
SET chat_id = (SELECT MIN(id) FROM chat_rooms) 
WHERE chat_id NOT IN (SELECT id FROM chat_rooms);

ALTER TABLE messages 
ADD CONSTRAINT fk_messages_chat 
FOREIGN KEY (chat_id) REFERENCES chat_rooms(id) ON DELETE CASCADE;


ALTER TABLE messages 
ADD CONSTRAINT fk_messages_sender 
FOREIGN KEY (sender_id) REFERENCES users(user_id) ON DELETE CASCADE;