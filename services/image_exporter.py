import os
import re
import sys
import unicodedata
import shutil
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

DEFAULT_FONT_FAMILY = "Arial"
MISSING_OUTPUT_DIR = "Output"
VACCINATED_OUTPUT_DIR = "Vaccinated"

def sanitize_filename(name):
    if not name: return "Khong_co_ten"
    name = str(name)
    name = unicodedata.normalize('NFKD', name).encode('ASCII', 'ignore').decode('utf-8')
    name = re.sub(r'[^\w\s-]', '', name).strip()
    name = re.sub(r'[-\s_]+', '_', name)
    return name if name else "Khong_co_ten"

def get_base_path():
    return os.path.dirname(os.path.abspath(sys.argv[0] if hasattr(sys, 'frozen') else __file__))

class ImageExportService:
    @staticmethod
    def generate_image(items_data, metadata, is_missing_list=True):
        try:
            patient_name = metadata.get('patient_name', '')
            patient_dob = metadata.get('patient_dob', '')
            
            dir_name = MISSING_OUTPUT_DIR if is_missing_list else VACCINATED_OUTPUT_DIR
            output_dir = os.path.join(get_base_path(), dir_name)
            os.makedirs(output_dir, exist_ok=True)
            
            base_name = sanitize_filename(patient_name or ("DS_Vac_xin_thieu" if is_missing_list else "DS_Vac_xin_da_tiem"))
            file_path = os.path.join(output_dir, f"{base_name}.png")
            counter = 1
            while os.path.exists(file_path):
                file_path = os.path.join(output_dir, f"{base_name}_{counter}.png")
                counter += 1

            scale = 4
            PADDING, ROW_HEIGHT, HEADER_HEIGHT = 40 * scale, 40 * scale, 55 * scale
            HEADER_BG, HEADER_FG, BORDER_COLOR = '#4F81BD', '#FFFFFF', '#95B3D7'
            ROW_EVEN_BG, ROW_ODD_BG, TEXT_COLOR, NOTE_COLOR = '#DCE6F1', '#FFFFFF', '#000000', '#555555'
            
            try:
                FONT_B = ImageFont.truetype("arialbd.ttf", 16 * scale)
                FONT_R = ImageFont.truetype("arial.ttf", 15 * scale)
                FONT_I = ImageFont.truetype("ariali.ttf", 12 * scale)
                FONT_TITLE = ImageFont.truetype("arialbd.ttf", 18 * scale)
                FONT_FOOTER = ImageFont.truetype("arial.ttf", 13 * scale)
            except IOError:
                FONT_B = FONT_R = FONT_TITLE = FONT_FOOTER = FONT_I = ImageFont.load_default()

            dummy_draw = ImageDraw.Draw(Image.new('RGB', (1, 1)))
            
            col_stt_w = dummy_draw.textbbox((0,0), "STT", font=FONT_B)[2] + (25 * scale)
            max_name_w = max(dummy_draw.textbbox((0,0), item['name'], font=FONT_R)[2] for item in items_data) if items_data else 0
            
            if is_missing_list:
                headers = ["STT", "Tên vắc xin", "Ngày có thể\ntiêm sớm nhất"]
                
                # Calculate header width considering multiple lines and Bold font
                header_date_lines = headers[2].split('\n')
                max_header_date_w = max(dummy_draw.textbbox((0,0), line, font=FONT_B)[2] for line in header_date_lines)
                content_date_w = dummy_draw.textbbox((0,0), "dd/mm/yyyy", font=FONT_R)[2]
                
                col_date_w = max(max_header_date_w, content_date_w) + (40 * scale)
                
                col_name_w = max(max_name_w, dummy_draw.textbbox((0,0), headers[1], font=FONT_B)[2]) + (40 * scale)
                col_widths = [col_stt_w, col_name_w, col_date_w]
            else:
                headers = ["STT", "Tên vắc xin", "Mũi", "Ngày tiêm", "Tuổi lúc tiêm"]
                col_dose_w = dummy_draw.textbbox((0,0), "Mũi", font=FONT_B)[2] + (30 * scale)
                col_date_w = dummy_draw.textbbox((0,0), "dd/mm/yyyy", font=FONT_R)[2] + (30 * scale)
                max_age_w = max(dummy_draw.textbbox((0,0), item.get('age', ''), font=FONT_R)[2] for item in items_data) if items_data else 0
                col_age_w = max(max_age_w, dummy_draw.textbbox((0,0), headers[4], font=FONT_B)[2]) + (30 * scale)
                col_name_w = max(max_name_w, dummy_draw.textbbox((0,0), headers[1], font=FONT_B)[2]) + (40 * scale)
                col_widths = [col_stt_w, col_name_w, col_dose_w, col_date_w, col_age_w]
            
            table_width = sum(col_widths)
            
            # Content width calculations
            title_text = "DANH SÁCH VẮC-XIN CẦN TIÊM" if is_missing_list else "DANH SÁCH VẮC-XIN ĐÃ TIÊM"
            title_w = dummy_draw.textbbox((0,0), title_text, font=FONT_TITLE)[2]
            
            disclaimer_text = "Ảnh chỉ mang tính chất tham khảo, để rõ hơn vui lòng liên hệ phòng tiêm."
            timestamp_text = f"Xuất ngày: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"
            disclaimer_w = dummy_draw.textbbox((0,0), disclaimer_text, font=FONT_I)[2]
            timestamp_w = dummy_draw.textbbox((0,0), timestamp_text, font=FONT_I)[2]
            
            footer_lines = ["Phòng tiêm chủng Vắc-xin Dịch Vụ Quế Võ", "SĐT: 0326286828", "Địa chỉ: Khu 4, Phố Mới, Quế Võ, Bắc Ninh"]
            max_footer_w = 0
            for line in footer_lines:
                fw = dummy_draw.textbbox((0,0), line, font=FONT_FOOTER)[2]
                if fw > max_footer_w: max_footer_w = fw

            # Final Image Width Calculation (Ensuring text fits)
            max_text_width = max(title_w, disclaimer_w, timestamp_w, max_footer_w)
            img_width = max(table_width, max_text_width) + (2 * PADDING)
            
            # Center alignment offset for table
            table_start_x = (img_width - table_width) / 2
            
            patient_h = (FONT_B.getbbox("A")[3] + (8 * scale)) * 2 if patient_name else (-15 * scale)
            disclaimer_h = FONT_I.getbbox("A")[3] + (5 * scale)
            footer_h = (FONT_FOOTER.getbbox("A")[3] + (5 * scale)) * 4 + disclaimer_h + (FONT_I.getbbox("A")[3] + (8 * scale))
            img_height = (2 * PADDING) + (60 * scale) + patient_h + HEADER_HEIGHT + (len(items_data) * ROW_HEIGHT) + (40 * scale) + footer_h

            img = Image.new('RGB', (int(img_width), int(img_height)), 'white')
            draw = ImageDraw.Draw(img)
            y = PADDING

            draw.text(((img_width - title_w) / 2, y), title_text, fill=TEXT_COLOR, font=FONT_TITLE)
            y += (60 * scale)

            if patient_name:
                draw.text((table_start_x, y), f"•  Tên người tiêm: {patient_name}", font=FONT_B, fill=TEXT_COLOR)
                y += FONT_B.getbbox("A")[3] + (8 * scale)
                draw.text((table_start_x, y), f"•  Ngày sinh: {patient_dob}", font=FONT_B, fill=TEXT_COLOR)
                y += FONT_B.getbbox("A")[3] + (25 * scale)

            x = table_start_x
            for i, header in enumerate(headers):
                draw.rectangle([x, y, x + col_widths[i], y + HEADER_HEIGHT], fill=HEADER_BG, outline=BORDER_COLOR)
                center_x = x + col_widths[i] / 2
                center_y = y + HEADER_HEIGHT / 2
                draw.multiline_text((center_x, center_y), header, font=FONT_B, fill=HEADER_FG, align="center", spacing=4 * scale, anchor="mm")
                x += col_widths[i]
            y += HEADER_HEIGHT

            for i, item in enumerate(items_data):
                row_bg = ROW_EVEN_BG if i % 2 == 0 else ROW_ODD_BG
                center_y_row = y + ROW_HEIGHT / 2
                x = table_start_x
                
                draw.rectangle([x, y, x + col_widths[0], y + ROW_HEIGHT], fill=row_bg, outline=BORDER_COLOR)
                draw.text((x + col_widths[0] / 2, center_y_row), str(i+1), font=FONT_R, fill=TEXT_COLOR, anchor="mm")
                x += col_widths[0]

                draw.rectangle([x, y, x + col_widths[1], y + ROW_HEIGHT], fill=row_bg, outline=BORDER_COLOR)
                draw.text((x + (15 * scale), center_y_row), item['name'], font=FONT_R, fill=TEXT_COLOR, anchor="lm")
                x += col_widths[1]

                if is_missing_list:
                    draw.rectangle([x, y, x + col_widths[2], y + ROW_HEIGHT], fill=row_bg, outline=BORDER_COLOR)
                    draw.text((x + col_widths[2] / 2, center_y_row), item['date'], font=FONT_R, fill=TEXT_COLOR, anchor="mm")
                else:
                    draw.rectangle([x, y, x + col_widths[2], y + ROW_HEIGHT], fill=row_bg, outline=BORDER_COLOR)
                    draw.text((x + col_widths[2] / 2, center_y_row), item['dose'], font=FONT_R, fill=TEXT_COLOR, anchor="mm")
                    x += col_widths[2]
                    
                    draw.rectangle([x, y, x + col_widths[3], y + ROW_HEIGHT], fill=row_bg, outline=BORDER_COLOR)
                    draw.text((x + col_widths[3] / 2, center_y_row), item['date'], font=FONT_R, fill=TEXT_COLOR, anchor="mm")
                    x += col_widths[3]
                    
                    draw.rectangle([x, y, x + col_widths[4], y + ROW_HEIGHT], fill=row_bg, outline=BORDER_COLOR)
                    draw.text((x + (15 * scale), center_y_row), item.get('age', ''), font=FONT_R, fill=TEXT_COLOR, anchor="lm")

                y += ROW_HEIGHT
            
            y += (20 * scale)
            draw.line([(PADDING, y), (img_width - PADDING, y)], fill='#AAAAAA', width=1 * scale)
            y += (10 * scale)
            
            draw.text(((img_width - disclaimer_w) / 2, y), disclaimer_text, font=FONT_I, fill=NOTE_COLOR)
            y += FONT_I.getbbox("A")[3] + (5 * scale)
            draw.text(((img_width - timestamp_w) / 2, y), timestamp_text, font=FONT_I, fill=NOTE_COLOR)
            y += FONT_I.getbbox("A")[3] + (15 * scale)

            for line in footer_lines:
                line_w = draw.textbbox((0,0), line, font=FONT_FOOTER)[2]
                draw.text(((img_width - line_w) / 2, y), line, font=FONT_FOOTER, fill=TEXT_COLOR)
                y += FONT_FOOTER.getbbox("A")[3] + (5 * scale)

            img.save(file_path)
            return file_path

        except Exception as e:
            raise Exception(f"Image generation failed: {str(e)}")

    @staticmethod
    def delete_images(is_missing_list=True):
        """Deletes all files in the target directory."""
        dir_name = MISSING_OUTPUT_DIR if is_missing_list else VACCINATED_OUTPUT_DIR
        folder_path = os.path.join(get_base_path(), dir_name)
        
        if not os.path.exists(folder_path):
            return 0, f"Thư mục '{dir_name}' không tồn tại."
            
        deleted_count = 0
        errors = []
        
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                    deleted_count += 1
            except Exception as e:
                errors.append(f"{filename}: {e}")
                
        if errors:
            return deleted_count, "\n".join(errors)
        return deleted_count, None