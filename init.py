import pymysql

def initialize_database():
    connection = pymysql.connect(host='localhost', user='root', password='689900')
    cursor = connection.cursor()

    try:
        # 创建数据库
        cursor.execute("DROP DATABASE IF EXISTS students;")
        cursor.execute("CREATE DATABASE IF NOT EXISTS students;")
        cursor.execute("USE students;")

        # 添加用户并设置密码
        try:
            cursor.execute("CREATE USER 'Admin'@'localhost' IDENTIFIED BY '111111';")
            cursor.execute("GRANT ALL PRIVILEGES ON students.* TO 'Admin'@'localhost';")
        except:
            pass

        try:
            cursor.execute("CREATE USER 'User'@'localhost' IDENTIFIED BY '111111';")
            cursor.execute("GRANT ALL PRIVILEGES ON students.* TO 'User'@'localhost';")
        except:
            pass

        # 创建学生表（S）
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS student (
            student_id INT AUTO_INCREMENT PRIMARY KEY,
            student_name VARCHAR(255) NOT NULL,
            student_age INT,
            gender VARCHAR(10),
            enrollment_year INT,
            major VARCHAR(255),
            average_grade FLOAT
        );
        ''')

        # 创建课程表（C）
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS course (
            course_id INT AUTO_INCREMENT PRIMARY KEY,
            course_name VARCHAR(255) NOT NULL
        );
        ''')

        # 创建选课记录表（SC）
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS student_course (
            student_id INT,
            course_id INT,
            grade INT,
            year INT,
            PRIMARY KEY (student_id, course_id),
            FOREIGN KEY (student_id) REFERENCES student(student_id) ON DELETE CASCADE,
            FOREIGN KEY (course_id) REFERENCES course(course_id) ON DELETE CASCADE,
            CHECK (grade >= 0 AND grade <= 100),
            CHECK (year >= (SELECT enrollment_year FROM student WHERE student_id = student_id))
        );
        ''')


        # 添加存储过程，用于计算学生平均成绩
        cursor.execute('''
        CREATE PROCEDURE calculate_average_grade(IN student_id_param INT)
        BEGIN
            DECLARE total_grade INT;
            DECLARE course_count INT;
            DECLARE avg_grade FLOAT;

            SELECT SUM(grade), COUNT(*) INTO total_grade, course_count
            FROM student_course
            WHERE student_id = student_id_param;

            IF course_count > 0 THEN
                SET avg_grade = total_grade / course_count;
            ELSE
                SET avg_grade = NULL;
            END IF;

            UPDATE student
            SET average_grade = avg_grade
            WHERE student_id = student_id_param;
        END;
        ''')

        # 添加触发器，用于在插入或更新选课记录时触发计算平均成绩的存储过程
        cursor.execute('''
        CREATE TRIGGER calculate_avg_grade_after_insert
        AFTER INSERT ON student_course
        FOR EACH ROW
        BEGIN
            CALL calculate_average_grade(NEW.student_id);
        END;
        ''')

        cursor.execute('''
        CREATE TRIGGER calculate_avg_grade_after_update
        AFTER UPDATE ON student_course
        FOR EACH ROW
        BEGIN
            CALL calculate_average_grade(NEW.student_id);
        END;
        ''')

        # 添加触发器，用于在删除选课记录时触发计算平均成绩的存储过程
        cursor.execute('''
        CREATE TRIGGER calculate_avg_grade_after_delete
        AFTER DELETE ON student_course
        FOR EACH ROW
        BEGIN
            CALL calculate_average_grade(OLD.student_id);
        END;
        ''')

        # 添加索引
        cursor.execute("CREATE INDEX idx_student_id ON student_course (student_id);")
        cursor.execute("CREATE INDEX idx_course_id ON student_course (course_id);")
        # 添加联合索引
        cursor.execute("CREATE INDEX idx_student_course ON student_course (student_id, course_id);")

        # 添加学生数据
        cursor.execute("INSERT INTO student (student_name, student_age, gender, enrollment_year, major) VALUES ('Alice', 20, 'Female', 2021, 'Computer Science')")
        cursor.execute("INSERT INTO student (student_name, student_age, gender, enrollment_year, major) VALUES ('Bob', 22, 'Male', 2020, 'Electrical Engineering')")
        cursor.execute("INSERT INTO student (student_name, student_age, gender, enrollment_year, major) VALUES ('Charlie', 21, 'Male', 2021, 'Mechanical Engineering')")
        cursor.execute("INSERT INTO student (student_name, student_age, gender, enrollment_year, major) VALUES ('David', 23, 'Male', 2019, 'Civil Engineering')")

        # 添加课程数据
        cursor.execute("INSERT INTO course (course_name) VALUES ('Database')")
        cursor.execute("INSERT INTO course (course_name) VALUES ('Computer Networks')")
        cursor.execute("INSERT INTO course (course_name) VALUES ('Artificial Intelligence')")
        cursor.execute("INSERT INTO course (course_name) VALUES ('Software Engineering')")
        cursor.execute("INSERT INTO course (course_name) VALUES ('Genshin Impact')")

        # 添加选课记录数据
        cursor.execute("INSERT INTO student_course (student_id, course_id, grade, year) VALUES (1, 1, 90, 2021)")
        cursor.execute("INSERT INTO student_course (student_id, course_id, grade, year) VALUES (2, 1, 85, 2021)")
        cursor.execute("INSERT INTO student_course (student_id, course_id, grade, year) VALUES (1, 2, 88, 2021)")
        cursor.execute("INSERT INTO student_course (student_id, course_id, grade, year) VALUES (2, 2, 92, 2021)")
        cursor.execute("INSERT INTO student_course (student_id, course_id, grade, year) VALUES (3, 3, 78, 2021)")
        cursor.execute("INSERT INTO student_course (student_id, course_id, grade, year) VALUES (4, 4, 95, 2021)")

        # cursor.execute("FLUSH PRIVILEGES;")

        connection.commit()

        print("数据库初始化成功！")

    except Exception as e:
        print(f"数据库初始化失败: {e}")

    finally:
        cursor.close()
        connection.close()

if __name__ == "__main__":
    initialize_database()
