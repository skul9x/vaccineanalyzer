import datetime
from services.base_db_service import BaseDbService
from services.data_formatter import DataFormattingService
from db_config import APP_SETTINGS

class VaccineService(BaseDbService):
    STATIC_APPOINTMENT_TYPES = [
        {'code': '20', 'name': 'abhayrab'},
        {'code': '15', 'name': 'BCG'},
        {'code': '26', 'name': 'boostrix'},
        {'code': '05', 'name': 'cúm'},
        {'code': '12', 'name': 'dại'},
        {'code': '23', 'name': 'engerix B 0.5'},
        {'code': '24', 'name': 'engerix B 1'},
        {'code': '10', 'name': 'gardasil'},
        {'code': '28', 'name': 'Hexaxim'},
        {'code': '19', 'name': 'imojev'},
        {'code': '22', 'name': 'indirab'},
        {'code': '29', 'name': 'infanrix hexa'},
        {'code': '39', 'name': 'influvac'},
        {'code': '41', 'name': 'menactra'},
        {'code': '40', 'name': 'mengoc bc'},
        {'code': '07', 'name': 'MMR'},
        {'code': '07', 'name': 'MMR-II'},
        {'code': '07', 'name': 'Priorix'},
        {'code': '31', 'name': 'pentaxim'},
        {'code': '03', 'name': 'Phế Cầu'},
        {'code': '36', 'name': 'prevenar 13'},
        {'code': '32', 'name': 'rotarix'},
        {'code': '33', 'name': 'rotateq'},
        {'code': '34', 'name': 'rotavin'},
        {'code': '11', 'name': 'sởi'},
        {'code': '35', 'name': 'synflorix'},
        {'code': '30', 'name': 'tetraxim'},
        {'code': '14', 'name': 'thuong hàn'},
        {'code': '01', 'name': 'Tiêm 6in1'},
        {'code': '17', 'name': 'varivax'},
        {'code': '04', 'name': 'VAT'},
        {'code': '37', 'name': 'vaxigrip 0.25'},
        {'code': '38', 'name': 'vaxigrip 0.5'},
        {'code': '21', 'name': 'verorab'},
        {'code': '42', 'name': 'VGA'},
        {'code': '13', 'name': 'viêm gan B'},
        {'code': '09', 'name': 'viêm não NB'}
    ]

    def get_vaccine_appointment_types(self):
        return self.STATIC_APPOINTMENT_TYPES

    def get_appt_code_by_name(self, vaccine_name):
        if not vaccine_name: return None
        
        name_norm = DataFormattingService.remove_vietnamese_accents(vaccine_name).lower()

        if any(x in name_norm for x in ['6 trong 1', '6in1', 'hexaxim', 'infanrix', 'quinvaxem', 'combe five', 'dpt-vgb-hib']):
            return '01'
        
        if 'prevenar 13' in name_norm or 'prevenar13' in name_norm:
            return '36'
        
        if 'synflorix' in name_norm:
            return '35'

        if any(x in name_norm for x in ['phe cau', 'prevenar', 'vaxneuvance', 'pneumovax']):
            return '03'
        
        if 'rota teq' in name_norm or 'rotateq' in name_norm: return '33'
        if 'rotarix' in name_norm: return '32'
        if 'rotavin' in name_norm: return '34' 
        if 'morcvax' in name_norm: return '33'
        
        if any(x in name_norm for x in ['viem gan a', 'avaxim', 'havax', 'twinrix']):
            return '42'

        if 'influvac' in name_norm: return '39'
        if 'vaxigrip' in name_norm:
            if '0.25' in name_norm: return '37'
            return '38'
        if any(x in name_norm for x in ['cum', 'gc flu']):
            return '05'

        if any(x in name_norm for x in ['thuong han', 'typhim']): return '14'

        if 'mmr' in name_norm or 'priorix' in name_norm:
            return '07'
        if 'soi' in name_norm and 'quai bi' in name_norm and 'rubella' in name_norm:
            return '07'

        if 'soi' in name_norm and 'rubella' not in name_norm and 'quai bi' not in name_norm:
            return '11'

        if 'menactra' in name_norm or 'acyw' in name_norm: return '41'
        if 'mengoc' in name_norm or 'bc' in name_norm: return '40'

        if 'imojev' in name_norm: return '19'
        if 'jeev' in name_norm: return '09'
        if any(x in name_norm for x in ['vnnb', 'jevax', 'viem nao']): return '09'

        if any(x in name_norm for x in ['thuy dau', 'varivax', 'varicella']):
            return '17'

        if any(x in name_norm for x in ['dai', 'verorab', 'abhayrab', 'indirab']):
            if 'abhayrab' in name_norm: return '20'
            if 'indirab' in name_norm: return '22'
            if 'verorab' in name_norm: return '21'
            return '12'

        if 'viem gan b' in name_norm or 'engerix' in name_norm or 'hepa' in name_norm:
            if 'engerix' in name_norm and '0.5' in name_norm: return '23'
            if 'engerix' in name_norm and '1' in name_norm: return '24'
            return '13'

        if 'pentaxim' in name_norm or '5 trong 1' in name_norm or '5in1' in name_norm:
            return '31'
        
        if 'vat' in name_norm or 'uon van' in name_norm:
            return '04'

        return None

    def schedule_appointment(self, ma_luotkham, id_benhnhan, vaccine_id, vaccine_name, days, appt_type_code, item_type="THUỐC/VẮC XIN", target_date=None):
        conn = None
        try:
            self.log(f"--- ĐẶT HẸN (F10) ---")
            self.log(f"Input: MaLK={ma_luotkham}, TypeCode={appt_type_code}")

            conn = self.get_connection()
            conn.autocommit = False 
            cursor = conn.cursor()
            
            user_name = APP_SETTINGS['USER_NAME']
            now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            if target_date:
                if isinstance(target_date, (datetime.date, datetime.datetime)):
                    appt_date = target_date
                else:
                    try:
                        appt_date = datetime.datetime.strptime(target_date, "%d/%m/%Y")
                    except:
                        appt_date = datetime.datetime.now() + datetime.timedelta(days=days)
            else:
                appt_date = datetime.datetime.now() + datetime.timedelta(days=days)
            
            appt_date_str = appt_date.strftime("%d/%m/%Y")
            self.log(f"Ngày hẹn: {appt_date_str}")
            
            sql_check_header = """
                SELECT id FROM kcb_phieuhen_tiemchung 
                WHERE ma_luotkham = ? AND ma_loaidvu_tiemchung = ?
            """
            cursor.execute(sql_check_header, (ma_luotkham, appt_type_code))
            row_header = cursor.fetchone()
            
            id_phieuhen = None
            if row_header:
                id_phieuhen = row_header[0]
                self.log(f"[INFO] Gộp vào phiếu hẹn cũ ID={id_phieuhen}")
            else:
                self.log(f"[INFO] Tạo phiếu hẹn mới cho loại: {appt_type_code}")
                sql_header = """
                    SET NOCOUNT ON;
                    INSERT INTO kcb_phieuhen_tiemchung (
                        id_benhnhan, ma_luotkham, ma_loaidvu_tiemchung, 
                        ngay_tao, nguoi_tao
                    ) 
                    OUTPUT INSERTED.id
                    VALUES (?, ?, ?, ?, ?);
                """
                try:
                    cursor.execute(sql_header, (id_benhnhan, ma_luotkham, appt_type_code, now_str, user_name))
                    row_h = cursor.fetchone()
                    if row_h: id_phieuhen = row_h[0]
                except: pass
                
                if not id_phieuhen:
                     cursor.execute("SELECT MAX(id) FROM kcb_phieuhen_tiemchung WHERE ma_luotkham = ?", (ma_luotkham,))
                     r = cursor.fetchone()
                     if r: id_phieuhen = r[0]

            if id_phieuhen:
                cursor.execute("SELECT COUNT(*) FROM kcb_phieuhen_tiemchung_chitiet WHERE id = ?", (id_phieuhen,))
                cnt = cursor.fetchone()[0]
                mui_thu = cnt + 1
                
                sql_detail = """
                    INSERT INTO kcb_phieuhen_tiemchung_chitiet (
                        id, mui_thu, ngay_hen, 
                        nguoi_tiem, ngay_tiem, 
                        trang_thai, ghi_chu
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """
                cursor.execute(sql_detail, (
                    id_phieuhen, 
                    mui_thu, 
                    appt_date, 
                    -1,
                    None,
                    0,
                    u'Đặt hẹn tự động (VaccineAnalyzer)'
                ))
                self.log(f"-> Tạo chi tiết hẹn thành công (Mũi {mui_thu} - {appt_date_str})")
            
            conn.commit()
            return True, f"Đã hẹn: {vaccine_name}\nNgày: {appt_date_str}"

        except Exception as e:
            if conn: conn.rollback()
            self.log(f"Lỗi đặt hẹn: {e}")
            return False, f"Lỗi SQL: {e}"
        finally:
            if conn: 
                try: conn.close()
                except: pass

    def get_future_appointments(self, id_benhnhan):
        if not id_benhnhan: return []
        
        appointments = []
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            sql = """
                SELECT h.ma_loaidvu_tiemchung, d.ngay_hen, h.id, d.mui_thu
                FROM kcb_phieuhen_tiemchung h
                JOIN kcb_phieuhen_tiemchung_chitiet d ON h.id = d.id
                WHERE h.id_benhnhan = ? 
                  AND d.ngay_hen > GETDATE()
                ORDER BY d.ngay_hen ASC
            """
            cursor.execute(sql, (id_benhnhan,))
            rows = cursor.fetchall()
            
            code_map = {item['code']: item['name'] for item in self.STATIC_APPOINTMENT_TYPES}
            
            for row in rows:
                code = row[0]
                date_val = row[1]
                header_id = row[2]
                mui_thu = row[3]
                
                vac_name = code_map.get(code, f"Mã {code}")
                
                date_str = ""
                if isinstance(date_val, (datetime.date, datetime.datetime)):
                    date_str = date_val.strftime("%d/%m/%Y")
                
                appointments.append({
                    "name": vac_name,
                    "date": date_str,
                    "code": code,
                    "header_id": header_id,
                    "mui_thu": mui_thu
                })
                
        except Exception as e:
            self.log(f"Error getting future appointments: {e}")
        finally:
            if conn: conn.close()
            
        return appointments

    def delete_appointment(self, header_id, mui_thu):
        conn = None
        try:
            conn = self.get_connection()
            conn.autocommit = False
            cursor = conn.cursor()
            
            sql = "DELETE FROM kcb_phieuhen_tiemchung_chitiet WHERE id = ? AND mui_thu = ?"
            cursor.execute(sql, (header_id, mui_thu))
            
            conn.commit()
            return True, "Đã xóa lịch hẹn."
        except Exception as e:
            if conn: conn.rollback()
            return False, f"Lỗi xóa: {e}"
        finally:
            if conn: conn.close()