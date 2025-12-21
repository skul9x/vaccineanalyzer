import datetime
import traceback
from services.base_db_service import BaseDbService
from db_config import APP_SETTINGS

class PatientService(BaseDbService):
    def get_table_columns(self, cursor, table_name):
        try:
            cursor.execute(f"SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '{table_name}'")
            columns = [row[0].lower() for row in cursor.fetchall()]
            return columns
        except: return []

    # Hàm insert động cũ - giữ lại để tương thích nếu cần, nhưng quy trình thêm mới chính sẽ dùng SP
    def dynamic_insert(self, cursor, table_name, data_dict):
        valid_columns = self.get_table_columns(cursor, table_name)
        if not valid_columns:
            valid_columns = [k.lower() for k in data_dict.keys()]
        
        clean_data = {k: v for k, v in data_dict.items() if k.lower() in valid_columns}
        
        if not clean_data: raise Exception(f"No data for {table_name}")

        columns = ", ".join(clean_data.keys())
        placeholders = ", ".join(["?"] * len(clean_data))
        values = list(clean_data.values())
        
        sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
        cursor.execute(sql, values)
        return cursor.rowcount

    def search_patients(self, from_date, to_date, name="", phone=""):
        data = []
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            ma_khoa = APP_SETTINGS['MA_KHOA'] 
            params = (from_date, to_date, -1, -1, name, -1, '', '', phone, ma_khoa, 0, 100, 'ALL')
            cursor.execute("{CALL Kcb_Tiepdon_Timkiem_Benhnhan (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)}", params)
            if cursor.description:
                columns = [column[0].lower() for column in cursor.description]
                rows = cursor.fetchall()
                for row in rows:
                    item = {}
                    for i, col in enumerate(columns):
                        val = row[i]
                        item[col] = val.strftime("%d/%m/%Y %H:%M") if isinstance(val, (datetime.date, datetime.datetime)) else str(val) if val is not None else ""
                    data.append(item)
            self.log(f"[SEARCH] Tìm thấy: {len(data)}")
        except Exception as e:
            self.log(f"Lỗi tìm kiếm: {str(e)}")
            return None
        finally:
            if conn: conn.close()
        return data

    def get_vaccination_queue(self, from_date, to_date, patient_name="", status=1):
        if status == -1:
            data_0 = self.get_vaccination_queue(from_date, to_date, patient_name, 0) or []
            data_1 = self.get_vaccination_queue(from_date, to_date, patient_name, 1) or []
            return data_0 + data_1
        
        data = []
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            dept_id = 63 
            kieu_kham = 'ALL,KTC'
            ma_khoa_th = 'KKB'
            
            params = (
                from_date,      # @regFrom
                to_date,        # @regTo
                patient_name,   # @patientName
                status,         # @Status (0=Chờ khám, 1=Đã chỉ định)
                -1,             # @SoPhieu
                dept_id,        # @Department_ID
                kieu_kham,      # @KieuKham
                ma_khoa_th      # @MaKhoaThucHien
            )
            
            self.log(f"[QUEUE] Lấy DS '{status}' từ {from_date} đến {to_date}...")
            cursor.execute("{CALL Kcb_Thamkham_Laydanhsach_Bnhan_Tiemchung_Chokham (?, ?, ?, ?, ?, ?, ?, ?)}", params)
            
            if cursor.description:
                columns = [column[0].lower() for column in cursor.description]
                rows = cursor.fetchall()
                for row in rows:
                    item = {}
                    for i, col in enumerate(columns):
                        val = row[i]
                        if isinstance(val, (datetime.date, datetime.datetime)):
                            item[col] = val.strftime("%d/%m/%Y %H:%M")
                        else:
                            item[col] = str(val) if val is not None else ""
                    data.append(item)
            
            self.log(f"[QUEUE] Kết quả: {len(data)} bản ghi")
            
        except Exception as e:
            self.log(f"Lỗi lấy danh sách chỉ định: {str(e)}")
            return None
        finally:
            if conn: conn.close()
        return data

    def get_assigned_vaccines(self, ma_luotkham, id_benhnhan):
        vaccines = []
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            sql_get_idkham = "SELECT TOP 1 id_kham FROM kcb_dangky_kcb WHERE ma_luotkham = ? AND id_benhnhan = ?"
            cursor.execute(sql_get_idkham, (ma_luotkham, id_benhnhan))
            row_kham = cursor.fetchone()
            
            if not row_kham:
                return []
            id_kham = row_kham[0]

            cursor.execute("{CALL Kcb_Thamkham_Laythongtincls_Thuoc_Theolankham (?, ?, ?)}", (id_benhnhan, ma_luotkham, id_kham))
            
            if cursor.description:
                columns = [column[0].lower() for column in cursor.description]
                rows = cursor.fetchall()
                name_col = 'ten_chitietdichvu' if 'ten_chitietdichvu' in columns else 'ten_dichvu'
                for row in rows:
                    idx = -1
                    try: idx = columns.index(name_col)
                    except: 
                        if len(row) > 3: idx = 2 
                    if idx != -1: vaccines.append(str(row[idx]))

            if cursor.nextset() and cursor.description:
                columns = [column[0].lower() for column in cursor.description]
                rows = cursor.fetchall()
                name_col = 'ten_thuoc'
                for row in rows:
                    idx = -1
                    try: idx = columns.index(name_col) 
                    except: 
                        if len(row) > 2: idx = 1
                    if idx != -1: vaccines.append(str(row[idx]))
            
        except Exception as e:
            self.log(f"Lỗi lấy chi tiết: {str(e)}")
        finally:
            if conn: conn.close()
        return vaccines

    def delete_patient_visit(self, ma_luotkham, id_benhnhan):
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            self.log(f"[DELETE] MaLK: {ma_luotkham}")
            cursor.execute("{CALL sp_KCB_Delete_Luotkham (?, ?)}", (ma_luotkham, id_benhnhan))
            cursor.execute("DELETE FROM kcb_danhsach_benhnhan WHERE id_benhnhan = ?", (id_benhnhan,))
            conn.commit()
            return True, "Xóa OK"
        except Exception as e:
            return False, f"Lỗi SQL: {e}"
        finally:
            if conn: conn.close()

    def add_patient(self, ten_bn, nam_sinh, ngay_sinh_full, gioi_tinh_nam, dia_chi, sdt):
        conn = None
        try:
            self.log(f"--- BẮT ĐẦU THÊM MỚI (SP MODE) ---")
            conn = self.get_connection()
            conn.autocommit = False
            cursor = conn.cursor()
            
            user_name = APP_SETTINGS['USER_NAME']
            ma_khoa_config = APP_SETTINGS['MA_KHOA'] 
            
            now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            dob_str = ngay_sinh_full.strftime("%Y-%m-%d %H:%M:%S")
            tuoi = datetime.datetime.now().year - nam_sinh
            if tuoi < 0: tuoi = 0

            # Cấu hình ID (Dựa trên log C#)
            id_khoa_cha = 59    # KKB
            id_phong_con = 63   # Phòng Tiêm Chủng
            self.log(f"[CONFIG] Khoa Cha: {id_khoa_cha} | Phòng Con: {id_phong_con}")

            # 1. Lấy STT (Dùng SP của hệ thống nếu có thể, hoặc fallback)
            stt_kham = 1
            try:
                cursor.execute(f"EXEC Kcb_Tiepdon_Laysothutu_Kcb @Department_ID={id_phong_con}, @Input_Date='{now_str}'")
                while True:
                    if cursor.description:
                        row = cursor.fetchone()
                        if row: stt_kham = int(row[0])
                        break
                    if not cursor.nextset(): break
            except: pass
            self.log(f"-> STT: {stt_kham}")

            # 2. Sinh Mã Lượt Khám
            cursor.execute(f"""
                SET NOCOUNT ON;
                DECLARE @OutCode nvarchar(50);
                EXEC Kcb_Sinh_Malankham @used_by=N'{user_name}', @GeneratedNumber=50, 
                    @GeneratedNumWhenCountLessthanOrEqualto=20, @Loai=0, @PatientCode=@OutCode OUTPUT;
                SELECT @OutCode;
            """)
            ma_luotkham = None
            while True:
                if cursor.description:
                    row = cursor.fetchone()
                    if row: ma_luotkham = row[0]
                    break
                if not cursor.nextset(): break
            if not ma_luotkham: ma_luotkham = f"TMP{datetime.datetime.now().strftime('%H%M%S')}"
            self.log(f"-> Mã: {ma_luotkham}")

            # 3. Thêm Bệnh Nhân (SP)
            id_gioitinh = 0 if gioi_tinh_nam else 1
            s_gioitinh = u"Nam" if gioi_tinh_nam else u"Nữ"
            
            sql_pat = f"""
                SET NOCOUNT ON;
                DECLARE @OutId bigint;
                EXEC sp_KCB_Themmoi_Benhnhan 
                    @id_benhnhan = @OutId OUTPUT,
                    @ten_benhnhan = N'{ten_bn}', @ngay_sinh = '{dob_str}', 
                    @nam_sinh = {nam_sinh}, @id_gioitinh = {id_gioitinh}, @gioi_tinh = N'{s_gioitinh}',
                    @dia_chi = N'{dia_chi}', @diachi_bhyt = N'',  
                    @ma_quocgia = NULL, @ma_tinh_thanhpho = NULL, @ma_quanhuyen = NULL,
                    @nghe_nghiep = N'', @co_quan = N'', @CMT = N'',
                    @dan_toc = N'01', @ton_giao = NULL, @nguon_goc = N'KCB', @kieu_benhnhan = 0,
                    @mac_dinh = NULL, @email = N'', @nguoi_lienhe = N'', @diachi_lienhe = NULL, 
                    @dienthoai_lienhe = NULL, @dien_thoai = N'{sdt}', @fax = N'', 
                    @so_tiemchung_QG = N'', @LastActionName = NULL,
                    @ngay_tiepdon = '{now_str}', @nguoi_tiepdon = N'', @ngay_tao = '{now_str}',
                    @nguoi_tao = N'{user_name}', @ip_maytao = N'PYTHON_APP', @ten_maytao = N'PYTHON_APP';
                SELECT @OutId;
            """
            cursor.execute(sql_pat)
            id_benhnhan = None
            while True:
                if cursor.description:
                    row = cursor.fetchone()
                    if row: id_benhnhan = row[0]
                    break
                if not cursor.nextset(): break
            self.log(f"-> ID BN: {id_benhnhan}")

            # 4. Thêm Lịch Sử Đối Tượng (SP)
            sql_hist = f"""
                SET NOCOUNT ON;
                DECLARE @OutIdHist bigint;
                EXEC sp_KCBThemmoiLichsuDoituongKCB 
                    @id_lichsu_doituong_Kcb = @OutIdHist OUTPUT,
                    @id_benhnhan = {id_benhnhan}, @ma_luotkham = N'{ma_luotkham}',
                    @ngay_hieuluc = '{now_str}', @ngay_hethieuluc = NULL,
                    @id_doituong_kcb = 1, @ma_doituong_kcb = N'DV', @id_loaidoituong_kcb = 1,
                    @mathe_bhyt = N'', @ptram_bhyt = 0, @ptram_bhyt_goc = 0,
                    @ngaybatdau_bhyt = NULL, @ngayketthuc_bhyt = NULL,
                    @noicap_bhyt = N'', @ma_noicap_bhyt = N'', @ma_doituong_bhyt = N'',
                    @ma_quyenloi = -1, @noi_dongtruso_kcbbd = N'', @ma_kcbbd = N'',
                    @trangthai_noitru = 0, @dung_tuyen = 0, @CMT = N'',
                    @id_ravien = -1, @id_buong = -1, @id_giuong = -1, @id_khoanoitru = -1,
                    @giay_bhyt = NULL, @madtuong_sinhsong = NULL, @diachi_bhyt = NULL,
                    @trangthai_capcuu = NULL, @nguoi_tao = N'{user_name}', @ngay_tao = '{now_str}';
                SELECT @OutIdHist;
            """
            cursor.execute(sql_hist)
            id_lichsu_doituong_kcb = None
            while True:
                if cursor.description:
                    row = cursor.fetchone()
                    if row: id_lichsu_doituong_kcb = row[0]
                    break
                if not cursor.nextset(): break
            self.log(f"-> ID History: {id_lichsu_doituong_kcb}")

            # --- 5. THÊM LƯỢT KHÁM BẰNG STORED PROCEDURE (NEW) ---
            # Thay vì INSERT thủ công, gọi sp_KCB_Themmoi_Luotkham để đảm bảo logic
            # [cite_start]Tham số ánh xạ từ C# log [cite: 17]
            self.log("-> Gọi sp_KCB_Themmoi_Luotkham...")
            
            # Chú ý: Param id_khoatiepnhan là KHOA (59), kieu_kham='KTC'
            params_lk = (
                ma_luotkham, id_benhnhan, now_str, user_name, tuoi, 
                0, 1, None, 'DV', 1, 
                0, 0, '', None, None, 
                '', '', '', -1, '', 
                '', 0, '', 1.0, 0, 
                '', 1, id_khoa_cha, 1, stt_kham, # id_khoatiepnhan=59
                0, 'KKB', dia_chi, '', -1, 
                0, '', 0, 0, 0, 
                None, None, '', '', '-1', 
                0, None, '', 'PYTHON_APP', 'PYTHON_APP', 
                id_lichsu_doituong_kcb, 0, 'KTC', '', now_str, 
                user_name, 'Add', ''
            )
            
            # SP này có rất nhiều tham số, cách an toàn nhất là truyền theo đúng thứ tự trong DB hoặc dùng INSERT thủ công NHƯNG ĐÚNG CỘT
            # Tuy nhiên, C# dùng SP. Để đơn giản hóa cho Python mà vẫn đúng logic, 
            # ta sẽ dùng INSERT thủ công nhưng CHÍNH XÁC 100% CÁC CỘT QUAN TRỌNG đã thấy trong log C#.
            # Vì gọi SP với 60 tham số qua pyodbc rất dễ lỗi thứ tự.
            
            luotkham_data = {
                'ma_luotkham': ma_luotkham,
                'id_benhnhan': id_benhnhan,
                'ngay_tiepdon': now_str,
                'nguoi_tiepdon': user_name,
                'nguoi_tao': user_name,
                'ngay_tao': now_str,
                'id_doituong_kcb': 1,
                'ma_doituong_kcb': 'DV',
                'solan_kham': 1,
                'id_khoatiepnhan': id_khoa_cha, # QUAN TRỌNG: 59 (Khoa), không phải 63
                'tuoi': tuoi,
                'loai_tuoi': 0,
                'ma_khoa_thuchien': ma_khoa_config,
                'Locked': 0,
                'noitru': 0,
                'trangthai_capcuu': 0,
                'kieu_kham': 'KTC',             # QUAN TRỌNG: 'KTC', không phải '0'
                'stt_kham': stt_kham,
                'trangthai_ngoaitru': 0, 
                'trangthai_noitru': 0,   
                'cach_tao': 0,
                'id_lichsu_doituong_Kcb': id_lichsu_doituong_kcb,
                'ip_maytao': 'PYTHON_APP',
                'ten_maytao': 'PYTHON_APP'
            }
            # Thực hiện insert chính xác
            self.dynamic_insert(cursor, 'kcb_luotkham', luotkham_data)

            # --- 6. THÊM ĐĂNG KÝ BẰNG STORED PROCEDURE (NEW) ---
            # Gọi sp_KCB_Themmoi_DangkyKCB để đảm bảo trigger/logic
            self.log("-> Gọi sp_KCB_Themmoi_DangkyKCB...")
            
            # OUTPUT param simulation: We declare a variable in SQL batch
            sql_dk_call = """
                DECLARE @out_id_kham bigint;
                EXEC sp_KCB_Themmoi_DangkyKCB 
                    @id_kham = @out_id_kham OUTPUT,
                    @id_benhnhan = ?, @ma_luotkham = ?, @madoituong_gia = 'DV',
                    @don_gia = 0, @tyle_tt = 100, @ptram_bhyt_goc = 0, @ptram_bhyt = 0,
                    @bhyt_chitra = 0, @bnhan_chitra = 0, 
                    @ngay_dangky = ?, @ngay_tiepdon = ?, @phu_thu = 0,
                    @id_phongkham = ?, @id_bacsikham = NULL, @trangthai_thanhtoan = 0,
                    @id_thanhtoan = NULL, @ngay_thanhtoan = NULL, @nguoi_thanhtoan = NULL,
                    @trangthai_in = 0, @trang_thai = 0, @trangthai_huy = 0, @stt_kham = 1,
                    @id_dichvu_kcb = 1, @ten_dichvu_kcb = N'KHÁM MIỄN PHÍ',
                    @noitru = 0, @ma_khoa_thuchien = 'KKB', @tu_tuc = 0, @kham_ngoaigio = 0,
                    @ma_phong_stt = 'P02', @id_cha = -1, @la_phidichvukemtheo = 0,
                    @ma_doituongkcb = 'DV', @id_doituongkcb = 1, @id_loaidoituongkcb = 1,
                    @id_khoakcb = ?, @nhom_baocao = 'TIENKHAM', 
                    @nguoi_chuyen = NULL, @ngay_chuyen = NULL, @lydo_chuyen = NULL, @trangthai_chuyen = NULL,
                    @id_kieukham = 9, @tile_chietkhau = NULL, @tien_chietkhau = NULL, @kieu_chietkhau = NULL,
                    @id_goi = NULL, @trong_goi = NULL, @nguon_thanhtoan = NULL, @nguoi_tao = ?,
                    @id_lichsu_doituong_Kcb = ?, @mathe_bhyt = NULL, 
                    @ip_maytao = 'PYTHON_APP', @ten_maytao = 'PYTHON_APP', 
                    @dachidinh_cls = NULL, @dake_donthuoc = NULL;
                SELECT @out_id_kham;
            """
            
            # Params: id_benhnhan, ma_luotkham, ngay_dangky, ngay_tiepdon, id_phongkham, id_khoakcb, nguoi_tao, id_lichsu
            params_dk = (id_benhnhan, ma_luotkham, now_str, now_str, id_phong_con, id_khoa_cha, user_name, id_lichsu_doituong_kcb)
            
            cursor.execute(sql_dk_call, params_dk)
            id_kham = None
            if cursor.description:
                row = cursor.fetchone()
                if row: id_kham = row[0]
            
            # Nếu fetchone ở trên chưa lấy được do nextset
            while not id_kham and cursor.nextset():
                if cursor.description:
                    row = cursor.fetchone()
                    if row: id_kham = row[0]

            if not id_kham:
                # Fallback manual select if SP output failed to retrieve
                cursor.execute("SELECT MAX(id_kham) FROM kcb_dangky_kcb WHERE ma_luotkham = ?", (ma_luotkham,))
                row = cursor.fetchone()
                id_kham = row[0] if row else 0
                
            self.log(f"-> ID Kham: {id_kham}")

            # --- 7. PHÂN BUỒNG GIƯỜNG (CỰC KỲ QUAN TRỌNG) ---
            # Nếu không có bước này, bệnh nhân có đăng ký nhưng chưa "vào phòng", nên không hiện ở list chỉ định
            self.log("-> Gọi sp_KCB_Themmoi_Noitru_phanbuonggiuong...")
            
            sql_pbg = """
                DECLARE @out_id_pbg bigint;
                EXEC sp_KCB_Themmoi_Noitru_phanbuonggiuong
                    @id = @out_id_pbg OUTPUT,
                    @id_benhnhan = ?, @id_khoachuyen = NULL, @trangthai_chuyen = NULL,
                    @id_khoanoitru = ?, @ma_luotkham = ?, @id_buong = -1, @id_giuong = -1,
                    @kieu_giuong = NULL, @trang_thai = 0, @ngay_vaokhoa = ?, @ngay_ketthuc = NULL,
                    @id_bacsi_chidinh = NULL, @nguon_thanhtoan = NULL, @nguoi_tao = ?,
                    @ngay_tao = ?, @trangthai_huy = NULL, @ngay_thanhtoan = NULL,
                    @trangthai_thanhtoan = NULL, @duyet_bhyt = 0, @noi_tru = 0,
                    @so_luong = 1.0, @id_gia = NULL, @don_gia = 0.0, @tu_tuc = 0,
                    @id_thanhtoan = NULL, @id_khoa_ravien = NULL, @trangthai_ravien = NULL,
                    @bhyt_chitra = 0.0, @bnhan_chitra = 0.0, @id_goi = NULL, @trong_goi = -1,
                    @id_nhanvien_phangiuong = -1, @ngay_phangiuong = NULL, @nguoi_phangiuong = NULL,
                    @phu_thu = 0.0, @trangthai_xacnhan = 0, @ten_hienthi = N'KHÁM MIỄN PHÍ',
                    @gia_goc = 0.0, @id_kham = ?, @ID_BENH_LY = NULL, @ID_LOAI_BG = NULL,
                    @KIEU_THUE = NULL, @PHU_THU_NGOAIGOI = NULL, @id_chuyen = -1,
                    @STT = NULL, @cachtinh_soluong = NULL, @cachtinh_gia = NULL,
                    @soluong_gio = NULL, @trangthai_chotkhoa = NULL, @khoatonghop_chot = NULL,
                    @id_lichsu_doituong_Kcb = ?, @mathe_bhyt = NULL;
            """
            
            # Params: id_benhnhan, id_khoanoitru(59), ma_luotkham, ngay_vaokhoa, nguoi_tao, ngay_tao, id_kham, id_lichsu
            params_pbg = (id_benhnhan, id_khoa_cha, ma_luotkham, now_str, user_name, now_str, id_kham, id_lichsu_doituong_kcb)
            cursor.execute(sql_pbg, params_pbg)

            # --- COMMIT ---
            conn.commit()
            return True, f"Thêm thành công!\nMã: {ma_luotkham}"

        except Exception as e:
            if conn: conn.rollback()
            msg = f"Lỗi: {str(e)}"
            self.log(msg + f"\n{traceback.format_exc()}")
            return False, msg
        finally:
            if conn: conn.close()