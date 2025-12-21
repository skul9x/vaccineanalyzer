import json
import os
import sys

def get_base_path():
    return os.path.dirname(os.path.abspath(sys.argv[0] if hasattr(sys, 'frozen') else __file__))

def get_vaccine_list():
    """
    Tải danh sách vắc-xin. Ưu tiên file 'vaccine_list.json' nằm cùng thư mục chạy.
    Nếu không có, sử dụng danh sách mặc định.
    """
    # Ưu tiên tìm file json cập nhật
    json_path = os.path.join(get_base_path(), "vaccine_list.json")
    if os.path.exists(json_path):
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list) and len(data) > 0:
                    return data
        except Exception as e:
            print(f"Lỗi đọc file vaccine_list.json: {e}")
    
    return DEFAULT_VACCINE_LIST

# Danh sách mặc định (Backup)
DEFAULT_VACCINE_LIST = [
    {
        "VACXIN_ID": 1,
        "TEN_VACXIN": "Viêm gan B sơ sinh",
        "TEN_THUONG_MAI": "Viêm gan B sơ sinh",
        "COVID": 0
    },
    {
        "VACXIN_ID": 2,
        "TEN_VACXIN": "BCG",
        "TEN_THUONG_MAI": "BCG",
        "COVID": 0
    },
    {
        "VACXIN_ID": 3,
        "TEN_VACXIN": "Quinvaxem",
        "TEN_THUONG_MAI": "Quinvaxem",
        "COVID": 0
    },
    {
        "VACXIN_ID": 4,
        "TEN_VACXIN": "OPV",
        "TEN_THUONG_MAI": "OPV",
        "COVID": 0
    },
    {
        "VACXIN_ID": 5,
        "TEN_VACXIN": "DPT",
        "TEN_THUONG_MAI": "DPT",
        "COVID": 0
    },
    {
        "VACXIN_ID": 6,
        "TEN_VACXIN": "Sởi",
        "TEN_THUONG_MAI": "Sởi",
        "COVID": 0
    },
    {
        "VACXIN_ID": 7,
        "TEN_VACXIN": "VNNB",
        "TEN_THUONG_MAI": "VNNB",
        "COVID": 0
    },
    {
        "VACXIN_ID": 8,
        "TEN_VACXIN": "Tả",
        "TEN_THUONG_MAI": "Tả",
        "COVID": 0
    },
    {
        "VACXIN_ID": 9,
        "TEN_VACXIN": "Thương hàn (Typhim Vi 10 ml)",
        "TEN_THUONG_MAI": "Typhim Vi (10 ml)",
        "COVID": 0
    },
    {
        "VACXIN_ID": 10,
        "TEN_VACXIN": "MR",
        "TEN_THUONG_MAI": "Sởi, Rubella",
        "COVID": 0
    },
    {
        "VACXIN_ID": 11,
        "TEN_VACXIN": "Pentaxim",
        "TEN_THUONG_MAI": "Pentaxim",
        "COVID": 0
    },
    {
        "VACXIN_ID": 12,
        "TEN_VACXIN": "Tetavax",
        "TEN_THUONG_MAI": "Tetavax",
        "COVID": 0
    },
    {
        "VACXIN_ID": 13,
        "TEN_VACXIN": "Priorix",
        "TEN_THUONG_MAI": "Priorix",
        "COVID": 0
    },
    {
        "VACXIN_ID": 15,
        "TEN_VACXIN": "ENGERIX-B 10mcg/0,5ml",
        "TEN_THUONG_MAI": "Engerix B",
        "COVID": 0
    },
    {
        "VACXIN_ID": 16,
        "TEN_VACXIN": "Euvax B  20mcg/1ml",
        "TEN_THUONG_MAI": "Euvax B  20mcg/1ml",
        "COVID": 0
    },
    {
        "VACXIN_ID": 17,
        "TEN_VACXIN": "ROTARIXTM",
        "TEN_THUONG_MAI": "Rotarix",
        "COVID": 0
    },
    {
        "VACXIN_ID": 18,
        "TEN_VACXIN": "Rota Teq",
        "TEN_THUONG_MAI": "Rota Teq",
        "COVID": 0
    },
    {
        "VACXIN_ID": 19,
        "TEN_VACXIN": "Rotavin-M1",
        "TEN_THUONG_MAI": "Rotavin-M1",
        "COVID": 0
    },
    {
        "VACXIN_ID": 20,
        "TEN_VACXIN": "Synflorix",
        "TEN_THUONG_MAI": "Synflorix",
        "COVID": 0
    },
    {
        "VACXIN_ID": 21,
        "TEN_VACXIN": "Infanrix Hexa",
        "TEN_THUONG_MAI": "Infanrix Hexa",
        "COVID": 0
    },
    {
        "VACXIN_ID": 22,
        "TEN_VACXIN": "Vaxigrip 0.25ml",
        "TEN_THUONG_MAI": "Vaxigrip 0.25ml",
        "COVID": 0
    },
    {
        "VACXIN_ID": 23,
        "TEN_VACXIN": "Influvac (Hộp 1 xy lanh)",
        "TEN_THUONG_MAI": "Influvax",
        "COVID": 0
    },
    {
        "VACXIN_ID": 24,
        "TEN_VACXIN": "VA - MENGOC - BC",
        "TEN_THUONG_MAI": "VA - MENGOC - BC",
        "COVID": 0
    },
    {
        "VACXIN_ID": 25,
        "TEN_VACXIN": "Meningo A+C",
        "TEN_THUONG_MAI": "Meningo A+C",
        "COVID": 0
    },
    {
        "VACXIN_ID": 26,
        "TEN_VACXIN": "Huyết Thanh Kháng Nọc Rắn Lục Tre",
        "TEN_THUONG_MAI": "Huyết Thanh Kháng Nọc Rắn Lục Tre",
        "COVID": 0
    },
    {
        "VACXIN_ID": 27,
        "TEN_VACXIN": "Huyết Thanh Kháng Nọc Rắn Hổ Đất",
        "TEN_THUONG_MAI": "Huyết Thanh Kháng Nọc Rắn Hổ Đất",
        "COVID": 0
    },
    {
        "VACXIN_ID": 32,
        "TEN_VACXIN": "MMR-II",
        "TEN_THUONG_MAI": "MMR-II",
        "COVID": 0
    },
    {
        "VACXIN_ID": 33,
        "TEN_VACXIN": "Varivax",
        "TEN_THUONG_MAI": "Varivax",
        "COVID": 0
    },
    {
        "VACXIN_ID": 34,
        "TEN_VACXIN": "Jevax (Lọ 5 liều 5ml)",
        "TEN_THUONG_MAI": "Jevax",
        "COVID": 0
    },
    {
        "VACXIN_ID": 35,
        "TEN_VACXIN": "Avaxim 160U",
        "TEN_THUONG_MAI": "Avaxim 160U",
        "COVID": 0
    },
    {
        "VACXIN_ID": 36,
        "TEN_VACXIN": "PNEUMO 23",
        "TEN_THUONG_MAI": "PNEUMO 23",
        "COVID": 0
    },
    {
        "VACXIN_ID": 38,
        "TEN_VACXIN": "Gardasil",
        "TEN_THUONG_MAI": "Gardasil",
        "COVID": 0
    },
    {
        "VACXIN_ID": 39,
        "TEN_VACXIN": "Cervarix",
        "TEN_THUONG_MAI": "Cervarix",
        "COVID": 0
    },
    {
        "VACXIN_ID": 40,
        "TEN_VACXIN": "Uốn ván",
        "TEN_THUONG_MAI": "Uốn ván",
        "COVID": 0
    },
    {
        "VACXIN_ID": 52,
        "TEN_VACXIN": "IPV",
        "TEN_THUONG_MAI": "IPV",
        "COVID": 0
    },
    {
        "VACXIN_ID": 53,
        "TEN_VACXIN": "Viêm gan B",
        "TEN_THUONG_MAI": "Viêm gan B",
        "COVID": 0
    },
    {
        "VACXIN_ID": 111,
        "TEN_VACXIN": "GC FLU Pre-filled Syringe",
        "TEN_THUONG_MAI": "GC FLU Pre-filled Syringe",
        "COVID": 0
    },
    {
        "VACXIN_ID": 171,
        "TEN_VACXIN": "Imojev",
        "TEN_THUONG_MAI": "Imojev",
        "COVID": 0
    },
    {
        "VACXIN_ID": 191,
        "TEN_VACXIN": "MENACTRA ",
        "TEN_THUONG_MAI": "MENACTRA ",
        "COVID": 0
    },
    {
        "VACXIN_ID": 208,
        "TEN_VACXIN": "Hepavax-Gene TF® Inj 20mcg/1ml",
        "TEN_THUONG_MAI": "Hepavax-Gene TF® Inj 20mcg/1ml",
        "COVID": 0
    },
    {
        "VACXIN_ID": 209,
        "TEN_VACXIN": "Hepavax-Gene TF® Inj 10mcg/0,5ml",
        "TEN_THUONG_MAI": "Hepavax-Gene TF® Inj 10mcg/0,5ml",
        "COVID": 0
    },
    {
        "VACXIN_ID": 210,
        "TEN_VACXIN": "TETANUS vaccine",
        "TEN_THUONG_MAI": "TETANUS vaccine",
        "COVID": 0
    },
    {
        "VACXIN_ID": 211,
        "TEN_VACXIN": "UV-BH (Td)",
        "TEN_THUONG_MAI": "UV-BH (Td)",
        "COVID": 0
    },
    {
        "VACXIN_ID": 212,
        "TEN_VACXIN": "ACT-HIB",
        "TEN_THUONG_MAI": "ACT-HIB",
        "COVID": 0
    },
    {
        "VACXIN_ID": 213,
        "TEN_VACXIN": "Hiberix",
        "TEN_THUONG_MAI": "Hiberix",
        "COVID": 0
    },
    {
        "VACXIN_ID": 214,
        "TEN_VACXIN": "Quimi-Hib",
        "TEN_THUONG_MAI": "Quimi-Hib",
        "COVID": 0
    },
    {
        "VACXIN_ID": 216,
        "TEN_VACXIN": "Trimovax Merieux (R.O.R)",
        "TEN_THUONG_MAI": "Trimovax Merieux (R.O.R)",
        "COVID": 0
    },
    {
        "VACXIN_ID": 217,
        "TEN_VACXIN": "Trivivac",
        "TEN_THUONG_MAI": "Trivivac",
        "COVID": 0
    },
    {
        "VACXIN_ID": 218,
        "TEN_VACXIN": "Rubella vaccine",
        "TEN_THUONG_MAI": "Rubella vaccine",
        "COVID": 0
    },
    {
        "VACXIN_ID": 219,
        "TEN_VACXIN": "Pavivac",
        "TEN_THUONG_MAI": "Pavivac",
        "COVID": 0
    },
    {
        "VACXIN_ID": 220,
        "TEN_VACXIN": "Mumps vaccine",
        "TEN_THUONG_MAI": "Mumps vaccine",
        "COVID": 0
    },
    {
        "VACXIN_ID": 221,
        "TEN_VACXIN": "MVVAC",
        "TEN_THUONG_MAI": "MVVAC",
        "COVID": 0
    },
    {
        "VACXIN_ID": 222,
        "TEN_VACXIN": "ROUVAX",
        "TEN_THUONG_MAI": "ROUVAX",
        "COVID": 0
    },
    {
        "VACXIN_ID": 223,
        "TEN_VACXIN": "Rimevax",
        "TEN_THUONG_MAI": "Rimevax",
        "COVID": 0
    },
    {
        "VACXIN_ID": 224,
        "TEN_VACXIN": "Measles vaccine",
        "TEN_THUONG_MAI": "Measles vaccine",
        "COVID": 0
    },
    {
        "VACXIN_ID": 225,
        "TEN_VACXIN": "Jebevax (Lọ 1 ml)",
        "TEN_THUONG_MAI": "Jebevax (Lọ 1 ml)",
        "COVID": 0
    },
    {
        "VACXIN_ID": 226,
        "TEN_VACXIN": "Boryung JE vaccine",
        "TEN_THUONG_MAI": "Boryung JE vaccine",
        "COVID": 0
    },
    {
        "VACXIN_ID": 227,
        "TEN_VACXIN": "JE vaccine",
        "TEN_THUONG_MAI": "JE vaccine",
        "COVID": 0
    },
    {
        "VACXIN_ID": 228,
        "TEN_VACXIN": "Orcvax",
        "TEN_THUONG_MAI": "Orcvax",
        "COVID": 0
    },
    {
        "VACXIN_ID": 229,
        "TEN_VACXIN": "Morcvax (Lọ 5 liều - 7.5ml)",
        "TEN_THUONG_MAI": "Morcvax (Lọ 5 liều - 7.5ml)",
        "COVID": 0
    },
    {
        "VACXIN_ID": 230,
        "TEN_VACXIN": "Influvac 2005/2006",
        "TEN_THUONG_MAI": "Influvac 2005/2006",
        "COVID": 0
    },
    {
        "VACXIN_ID": 231,
        "TEN_VACXIN": "Fluarix 0.5ml",
        "TEN_THUONG_MAI": "Fluarix 0.5ml",
        "COVID": 0
    },
    {
        "VACXIN_ID": 232,
        "TEN_VACXIN": "Inflexal V ",
        "TEN_THUONG_MAI": "Inflexal V ",
        "COVID": 0
    },
    {
        "VACXIN_ID": 233,
        "TEN_VACXIN": "Verorab 0.5ml",
        "TEN_THUONG_MAI": "Verorab 0.5ml",
        "COVID": 0
    },
    {
        "VACXIN_ID": 234,
        "TEN_VACXIN": "Rabipur.",
        "TEN_THUONG_MAI": "Rabipur.",
        "COVID": 0
    },
    {
        "VACXIN_ID": 235,
        "TEN_VACXIN": "Rabies vaccine",
        "TEN_THUONG_MAI": "Rabies vaccine",
        "COVID": 0
    },
    {
        "VACXIN_ID": 236,
        "TEN_VACXIN": "PNEUMO 24",
        "TEN_THUONG_MAI": "PNEUMO 24",
        "COVID": 0
    },
    {
        "VACXIN_ID": 237,
        "TEN_VACXIN": "SAT 1500IU",
        "TEN_THUONG_MAI": "SAT 1500IU",
        "COVID": 0
    },
    {
        "VACXIN_ID": 238,
        "TEN_VACXIN": "HT Uốn Ván 1500 IU",
        "TEN_THUONG_MAI": "HT Uốn Ván 1500 IU",
        "COVID": 0
    },
    {
        "VACXIN_ID": 239,
        "TEN_VACXIN": "TETANEA  1500UI",
        "TEN_THUONG_MAI": "TETANEA  1500UI",
        "COVID": 0
    },
    {
        "VACXIN_ID": 240,
        "TEN_VACXIN": "TETANUS Antitoxin  (A.T.S)",
        "TEN_THUONG_MAI": "TETANUS Antitoxin  (A.T.S)",
        "COVID": 0
    },
    {
        "VACXIN_ID": 241,
        "TEN_VACXIN": "ANTITETA II. 1500IU",
        "TEN_THUONG_MAI": "ANTITETA II. 1500IU",
        "COVID": 0
    },
    {
        "VACXIN_ID": 242,
        "TEN_VACXIN": "SAR 1000IU",
        "TEN_THUONG_MAI": "SAR 1000IU",
        "COVID": 0
    },
    {
        "VACXIN_ID": 243,
        "TEN_VACXIN": "FAVIRAB",
        "TEN_THUONG_MAI": "FAVIRAB",
        "COVID": 0
    },
    {
        "VACXIN_ID": 244,
        "TEN_VACXIN": "Anti-Rab 1000IU",
        "TEN_THUONG_MAI": "Anti-Rab 1000IU",
        "COVID": 0
    },
    {
        "VACXIN_ID": 246,
        "TEN_VACXIN": "Vắc xin uốn ván bạch hầu hấp phụ (Td) (Hộp 20 ống 0.5ml)",
        "TEN_THUONG_MAI": "Vắc xin uốn ván bạch hầu hấp phụ (Td) (Hộp 20 ống 0.5ml)",
        "COVID": 0
    },
    {
        "VACXIN_ID": 247,
        "TEN_VACXIN": "r-Hbvax (1ml)",
        "TEN_THUONG_MAI": "r-Hbvax (1ml)",
        "COVID": 0
    },
    {
        "VACXIN_ID": 249,
        "TEN_VACXIN": "Biosubtyl DL (Hộp 10 gói)",
        "TEN_THUONG_MAI": "Biosubtyl DL (Hộp 10 gói)",
        "COVID": 0
    },
    {
        "VACXIN_ID": 250,
        "TEN_VACXIN": "Fluarix 0.25ml",
        "TEN_THUONG_MAI": "Fluarix 0.25ml",
        "COVID": 0
    },
    {
        "VACXIN_ID": 251,
        "TEN_VACXIN": "TETRACT - HIB (Lọ 10 liều)",
        "TEN_THUONG_MAI": "TETRACT - HIB (Lọ 10 liều)",
        "COVID": 0
    },
    {
        "VACXIN_ID": 252,
        "TEN_VACXIN": "Jevax (Lọ 1 liều 1ml)",
        "TEN_THUONG_MAI": "Jevax (Lọ 1 liều 1ml)",
        "COVID": 0
    },
    {
        "VACXIN_ID": 253,
        "TEN_VACXIN": "Morcvax (Lọ 1 liều - 1.5ml)",
        "TEN_THUONG_MAI": "Morcvax (Lọ 1 liều - 1.5ml)",
        "COVID": 0
    },
    {
        "VACXIN_ID": 254,
        "TEN_VACXIN": "Imovax Polio (Lọ 10 liều)- TCDV",
        "TEN_THUONG_MAI": "Imovax Polio (Lọ 10 liều)- TCDV",
        "COVID": 0
    },
    {
        "VACXIN_ID": 255,
        "TEN_VACXIN": "Vắc xin uốn ván hấp phụ (TT) (Lọ 20 liều)",
        "TEN_THUONG_MAI": "Vắc xin uốn ván hấp phụ (TT) (Lọ 20 liều)",
        "COVID": 0
    },
    {
        "VACXIN_ID": 256,
        "TEN_VACXIN": "Eriprove (Lọ 1 liều 0.5ml 2000IU)",
        "TEN_THUONG_MAI": "Eriprove (Lọ 1 liều 0.5ml 2000IU)",
        "COVID": 0
    },
    {
        "VACXIN_ID": 257,
        "TEN_VACXIN": "Eriprove (Lọ 1 liều 0.5ml 1000IU)",
        "TEN_THUONG_MAI": "Eriprove (Lọ 1 liều 0.5ml 1000IU)",
        "COVID": 0
    },
    {
        "VACXIN_ID": 258,
        "TEN_VACXIN": "Eriprove (Lọ 1 liều 1ml 4000IU)",
        "TEN_THUONG_MAI": "Eriprove (Lọ 1 liều 1ml 4000IU)",
        "COVID": 0
    },
    {
        "VACXIN_ID": 259,
        "TEN_VACXIN": "ERITROGEN 2000IU",
        "TEN_THUONG_MAI": "ERITROGEN 2000IU",
        "COVID": 0
    },
    {
        "VACXIN_ID": 260,
        "TEN_VACXIN": "Epocassa 2000IU",
        "TEN_THUONG_MAI": "Epocassa 2000IU",
        "COVID": 0
    },
    {
        "VACXIN_ID": 261,
        "TEN_VACXIN": "Epocassa 10000IU",
        "TEN_THUONG_MAI": "Epocassa 10000IU",
        "COVID": 0
    },
    {
        "VACXIN_ID": 262,
        "TEN_VACXIN": "Vắc xin thương hàn vi Polysaccharide (Lọ 1ml)",
        "TEN_THUONG_MAI": "Vắc xin thương hàn vi Polysaccharide (Lọ 1ml)",
        "COVID": 0
    },
    {
        "VACXIN_ID": 263,
        "TEN_VACXIN": "Vắc xin thương hàn vi Polysaccharide (Lọ 2.5ml)",
        "TEN_THUONG_MAI": "Vắc xin thương hàn vi Polysaccharide (Lọ 2.5ml)",
        "COVID": 0
    },
    {
        "VACXIN_ID": 264,
        "TEN_VACXIN": "Vắc xin thương hàn vi Polysaccharide (Lọ 10ml)",
        "TEN_THUONG_MAI": "Vắc xin thương hàn vi Polysaccharide (Lọ 10ml)",
        "COVID": 0
    },
    {
        "VACXIN_ID": 265,
        "TEN_VACXIN": "Vắc xin uốn ván bạch hầu hấp phụ (Td) (Hộp 10 lọ 5ml)",
        "TEN_THUONG_MAI": "Vắc xin uốn ván bạch hầu hấp phụ (Td) (Hộp 10 lọ 5ml)",
        "COVID": 0
    },
    {
        "VACXIN_ID": 266,
        "TEN_VACXIN": "r-Hbvax (0.5ml)",
        "TEN_THUONG_MAI": "r-Hbvax (0.5ml)",
        "COVID": 0
    },
    {
        "VACXIN_ID": 267,
        "TEN_VACXIN": "Biosubtyl DL (Hộp 20 gói)",
        "TEN_THUONG_MAI": "Biosubtyl DL (Hộp 20 gói)",
        "COVID": 0
    },
    {
        "VACXIN_ID": 268,
        "TEN_VACXIN": "Biosubtyl DL (Hộp 25 gói)",
        "TEN_THUONG_MAI": "Biosubtyl DL (Hộp 25 gói)",
        "COVID": 0
    },
    {
        "VACXIN_ID": 281,
        "TEN_VACXIN": "VARILRIX",
        "TEN_THUONG_MAI": "VARILRIX",
        "COVID": 0
    },
    {
        "VACXIN_ID": 282,
        "TEN_VACXIN": "OKAVAX",
        "TEN_THUONG_MAI": "OKAVAX",
        "COVID": 0
    },
    {
        "VACXIN_ID": 283,
        "TEN_VACXIN": "Avaxim 80U",
        "TEN_THUONG_MAI": "Avaxim 80U",
        "COVID": 0
    },
    {
        "VACXIN_ID": 284,
        "TEN_VACXIN": "HAVAX",
        "TEN_THUONG_MAI": "HAVAX",
        "COVID": 0
    },
    {
        "VACXIN_ID": 285,
        "TEN_VACXIN": "Epaxal",
        "TEN_THUONG_MAI": "Epaxal",
        "COVID": 0
    },
    {
        "VACXIN_ID": 286,
        "TEN_VACXIN": "HAVRIX",
        "TEN_THUONG_MAI": "HAVRIX",
        "COVID": 0
    },
    {
        "VACXIN_ID": 287,
        "TEN_VACXIN": "Twinrix",
        "TEN_THUONG_MAI": "Twinrix",
        "COVID": 0
    },
    {
        "VACXIN_ID": 288,
        "TEN_VACXIN": "VIVAXIM",
        "TEN_THUONG_MAI": "VIVAXIM",
        "COVID": 0
    },
    {
        "VACXIN_ID": 289,
        "TEN_VACXIN": "Zerotyph cap",
        "TEN_THUONG_MAI": "Zerotyph cap",
        "COVID": 0
    },
    {
        "VACXIN_ID": 290,
        "TEN_VACXIN": "TYPHERIX",
        "TEN_THUONG_MAI": "TYPHERIX",
        "COVID": 0
    },
    {
        "VACXIN_ID": 291,
        "TEN_VACXIN": "VI vaccine",
        "TEN_THUONG_MAI": "VI vaccine",
        "COVID": 0
    },
    {
        "VACXIN_ID": 292,
        "TEN_VACXIN": "Heberbiovac HB 10mcg/0,5ml ",
        "TEN_THUONG_MAI": "Heberbiovac HB 10mcg/0,5ml ",
        "COVID": 0
    },
    {
        "VACXIN_ID": 293,
        "TEN_VACXIN": "Heberbiovac HB 20mcg/1ml ",
        "TEN_THUONG_MAI": "Heberbiovac HB 20mcg/1ml ",
        "COVID": 0
    },
    {
        "VACXIN_ID": 294,
        "TEN_VACXIN": "ENGERIX-B 20mcg/1ml",
        "TEN_THUONG_MAI": "ENGERIX-B 20mcg/1ml",
        "COVID": 0
    },
    {
        "VACXIN_ID": 295,
        "TEN_VACXIN": "H-B-VAX II",
        "TEN_THUONG_MAI": "H-B-VAX II",
        "COVID": 0
    },
    {
        "VACXIN_ID": 296,
        "TEN_VACXIN": "Euvax B 10mcg/0,5ml",
        "TEN_THUONG_MAI": "Euvax B 10mcg/0,5ml",
        "COVID": 0
    },
    {
        "VACXIN_ID": 297,
        "TEN_VACXIN": "r-HBvax",
        "TEN_THUONG_MAI": "r-HBvax",
        "COVID": 0
    },
    {
        "VACXIN_ID": 298,
        "TEN_VACXIN": "SCI-B-VAC 5mg/0.5ml",
        "TEN_THUONG_MAI": "SCI-B-VAC 5mg/0.5ml",
        "COVID": 0
    },
    {
        "VACXIN_ID": 299,
        "TEN_VACXIN": "SCI-B-VAC 10mg/1ml",
        "TEN_THUONG_MAI": "SCI-B-VAC 10mg/1ml",
        "COVID": 0
    },
    {
        "VACXIN_ID": 300,
        "TEN_VACXIN": "Gene-HBvax (Lọ 0.5ml)",
        "TEN_THUONG_MAI": "Gene-HBvax (Lọ 0.5ml)",
        "COVID": 0
    },
    {
        "VACXIN_ID": 301,
        "TEN_VACXIN": "HEPA- B- VAC",
        "TEN_THUONG_MAI": "HEPA- B- VAC",
        "COVID": 0
    },
    {
        "VACXIN_ID": 302,
        "TEN_VACXIN": "HBVaxPRO",
        "TEN_THUONG_MAI": "HBVaxPRO",
        "COVID": 0
    },
    {
        "VACXIN_ID": 303,
        "TEN_VACXIN": "TRITANRIX-HB",
        "TEN_THUONG_MAI": "TRITANRIX-HB",
        "COVID": 0
    },
    {
        "VACXIN_ID": 304,
        "TEN_VACXIN": "TETRACT - HIB (Lọ 1 liều)",
        "TEN_THUONG_MAI": "TETRACT - HIB (Lọ 1 liều)",
        "COVID": 0
    },
    {
        "VACXIN_ID": 305,
        "TEN_VACXIN": "DTCOQ",
        "TEN_THUONG_MAI": "DTCOQ",
        "COVID": 0
    },
    {
        "VACXIN_ID": 306,
        "TEN_VACXIN": "Tetraxim",
        "TEN_THUONG_MAI": "Tetraxim",
        "COVID": 0
    },
    {
        "VACXIN_ID": 307,
        "TEN_VACXIN": "Hexavac",
        "TEN_THUONG_MAI": "Hexavac",
        "COVID": 0
    },
    {
        "VACXIN_ID": 308,
        "TEN_VACXIN": "VAT (ống 1 liều)",
        "TEN_THUONG_MAI": "VAT (ống 1 liều)",
        "COVID": 0
    },
    {
        "VACXIN_ID": 309,
        "TEN_VACXIN": "D.T.VAX",
        "TEN_THUONG_MAI": "D.T.VAX",
        "COVID": 0
    },
    {
        "VACXIN_ID": 310,
        "TEN_VACXIN": "Imovax Polio (Lọ 1 liều)- TCDV ",
        "TEN_THUONG_MAI": "Imovax Polio (Lọ 1 liều)- TCDV ",
        "COVID": 0
    },
    {
        "VACXIN_ID": 311,
        "TEN_VACXIN": "Abhayrab 0.5ml",
        "TEN_THUONG_MAI": "Abhayrab 0.5ml",
        "COVID": 0
    },
    {
        "VACXIN_ID": 312,
        "TEN_VACXIN": "VAXIGRIP 0.5ml ",
        "TEN_THUONG_MAI": "VAXIGRIP 0.5ml ",
        "COVID": 0
    },
    {
        "VACXIN_ID": 313,
        "TEN_VACXIN": "Rubella",
        "TEN_THUONG_MAI": "Rubella",
        "COVID": 0
    },
    {
        "VACXIN_ID": 314,
        "TEN_VACXIN": "Varicella ",
        "TEN_THUONG_MAI": "Varicella ",
        "COVID": 0
    },
    {
        "VACXIN_ID": 315,
        "TEN_VACXIN": "Adacel",
        "TEN_THUONG_MAI": "Adacel",
        "COVID": 0
    },
    {
        "VACXIN_ID": 316,
        "TEN_VACXIN": "HEPABIG 100.I.U./0,5ml",
        "TEN_THUONG_MAI": "HEPABIG 100.I.U./0,5ml",
        "COVID": 0
    },
    {
        "VACXIN_ID": 317,
        "TEN_VACXIN": "ImmunoHbs - 180 IU/ml",
        "TEN_THUONG_MAI": "ImmunoHbs - 180 IU/ml",
        "COVID": 0
    },
    {
        "VACXIN_ID": 318,
        "TEN_VACXIN": "Lyssavac",
        "TEN_THUONG_MAI": "Lyssavac",
        "COVID": 0
    },
    {
        "VACXIN_ID": 319,
        "TEN_VACXIN": "Stamaril",
        "TEN_THUONG_MAI": "Stamaril",
        "COVID": 0
    },
    {
        "VACXIN_ID": 320,
        "TEN_VACXIN": "R.S.Jev",
        "TEN_THUONG_MAI": "R.S.Jev",
        "COVID": 0
    },
    {
        "VACXIN_ID": 321,
        "TEN_VACXIN": "Influvac 2014/2015",
        "TEN_THUONG_MAI": "Influvac 2014/2015",
        "COVID": 0
    },
    {
        "VACXIN_ID": 323,
        "TEN_VACXIN": "RS JEV",
        "TEN_THUONG_MAI": "RS JEV",
        "COVID": 0
    },
    {
        "VACXIN_ID": 324,
        "TEN_VACXIN": "Japanese Encephalitis vaccine-GCC",
        "TEN_THUONG_MAI": "Japanese Encephalitis vaccine-GCC",
        "COVID": 0
    },
    {
        "VACXIN_ID": 325,
        "TEN_VACXIN": "Agrippal S1",
        "TEN_THUONG_MAI": "Agrippal S1",
        "COVID": 0
    },
    {
        "VACXIN_ID": 326,
        "TEN_VACXIN": "VIVOTIF",
        "TEN_THUONG_MAI": "VIVOTIF",
        "COVID": 0
    },
    {
        "VACXIN_ID": 327,
        "TEN_VACXIN": "Polysaccharide meningococcal A+C",
        "TEN_THUONG_MAI": "Polysaccharide meningococcal A+C",
        "COVID": 0
    },
    {
        "VACXIN_ID": 328,
        "TEN_VACXIN": "Vắc xin uốn ván hấp phụ (TT) (Lọ 1 liều)",
        "TEN_THUONG_MAI": "Vắc xin uốn ván hấp phụ (TT) (Lọ 1 liều)",
        "COVID": 0
    },
    {
        "VACXIN_ID": 329,
        "TEN_VACXIN": "Eriprove (Lọ 1 liều 1ml 2000IU)",
        "TEN_THUONG_MAI": "Eriprove (Lọ 1 liều 1ml 2000IU)",
        "COVID": 0
    },
    {
        "VACXIN_ID": 330,
        "TEN_VACXIN": "Relipoietin 10000U",
        "TEN_THUONG_MAI": "Relipoietin 10000U",
        "COVID": 0
    },
    {
        "VACXIN_ID": 331,
        "TEN_VACXIN": "Relipoietin 4000U",
        "TEN_THUONG_MAI": "Relipoietin 4000U",
        "COVID": 0
    },
    {
        "VACXIN_ID": 332,
        "TEN_VACXIN": "Heberitro 2000IU",
        "TEN_THUONG_MAI": "Heberitro 2000IU",
        "COVID": 0
    },
    {
        "VACXIN_ID": 333,
        "TEN_VACXIN": "ERITROGEN 4000IU",
        "TEN_THUONG_MAI": "ERITROGEN 4000IU",
        "COVID": 0
    },
    {
        "VACXIN_ID": 334,
        "TEN_VACXIN": "Hemapo 10000IU",
        "TEN_THUONG_MAI": "Hemapo 10000IU",
        "COVID": 0
    },
    {
        "VACXIN_ID": 335,
        "TEN_VACXIN": "Hemapo 3000IU",
        "TEN_THUONG_MAI": "Hemapo 3000IU",
        "COVID": 0
    },
    {
        "VACXIN_ID": 336,
        "TEN_VACXIN": "Hemapo 2000IU",
        "TEN_THUONG_MAI": "Hemapo 2000IU",
        "COVID": 0
    },
    {
        "VACXIN_ID": 337,
        "TEN_VACXIN": "Genoepo 2000IU",
        "TEN_THUONG_MAI": "Genoepo 2000IU",
        "COVID": 0
    },
    {
        "VACXIN_ID": 338,
        "TEN_VACXIN": "Genoepo 4000IU",
        "TEN_THUONG_MAI": "Genoepo 4000IU",
        "COVID": 0
    },
    {
        "VACXIN_ID": 339,
        "TEN_VACXIN": "Epocassa 4000IU",
        "TEN_THUONG_MAI": "Epocassa 4000IU",
        "COVID": 0
    },
    {
        "VACXIN_ID": 340,
        "TEN_VACXIN": "Epokine Prefilled injection 2000IU/0,5ml",
        "TEN_THUONG_MAI": "Epokine Prefilled injection 2000IU/0,5ml",
        "COVID": 0
    },
    {
        "VACXIN_ID": 341,
        "TEN_VACXIN": "Epotiv Inj. 2000IU",
        "TEN_THUONG_MAI": "Epotiv Inj. 2000IU",
        "COVID": 0
    },
    {
        "VACXIN_ID": 342,
        "TEN_VACXIN": "Epotiv Inj. 4000IU",
        "TEN_THUONG_MAI": "Epotiv Inj. 4000IU",
        "COVID": 0
    },
    {
        "VACXIN_ID": 343,
        "TEN_VACXIN": "Ior Epocim-2000",
        "TEN_THUONG_MAI": "Ior Epocim-2000",
        "COVID": 0
    },
    {
        "VACXIN_ID": 344,
        "TEN_VACXIN": "Nanokine 4000IU ",
        "TEN_THUONG_MAI": "Nanokine 4000IU ",
        "COVID": 0
    },
    {
        "VACXIN_ID": 345,
        "TEN_VACXIN": "Nanokine 2000IU",
        "TEN_THUONG_MAI": "Nanokine 2000IU",
        "COVID": 0
    },
    {
        "VACXIN_ID": 346,
        "TEN_VACXIN": "Nanokine 10000IU",
        "TEN_THUONG_MAI": "Nanokine 10000IU",
        "COVID": 0
    },
    {
        "VACXIN_ID": 347,
        "TEN_VACXIN": "Vắc xin thương hàn vi Polysaccharide (Lọ 0.5ml)",
        "TEN_THUONG_MAI": "Vắc xin thương hàn vi Polysaccharide (Lọ 0.5ml)",
        "COVID": 0
    },
    {
        "VACXIN_ID": 348,
        "TEN_VACXIN": "Biosubtyl DL (Hộp 30 gói)",
        "TEN_THUONG_MAI": "Biosubtyl DL (Hộp 30 gói)",
        "COVID": 0
    },
    {
        "VACXIN_ID": 349,
        "TEN_VACXIN": "Biosubtyl DL (Hộp 50 gói)",
        "TEN_THUONG_MAI": "Biosubtyl DL (Hộp 50 gói)",
        "COVID": 0
    },
    {
        "VACXIN_ID": 350,
        "TEN_VACXIN": "Biosubtyl DL (Thùng 50 hộp)",
        "TEN_THUONG_MAI": "Biosubtyl DL (Thùng 50 hộp)",
        "COVID": 0
    },
    {
        "VACXIN_ID": 351,
        "TEN_VACXIN": "DPT (Lọ 2 liều)",
        "TEN_THUONG_MAI": "DPT (Lọ 2 liều)",
        "COVID": 0
    },
    {
        "VACXIN_ID": 353,
        "TEN_VACXIN": "Gene-HBvax (Lọ 1ml)",
        "TEN_THUONG_MAI": "Gene-HBvax (Lọ 1ml)",
        "COVID": 0
    },
    {
        "VACXIN_ID": 354,
        "TEN_VACXIN": "Jebevax (Lọ 5 ml)",
        "TEN_THUONG_MAI": "Jebevax (Lọ 5 ml)",
        "COVID": 0
    },
    {
        "VACXIN_ID": 355,
        "TEN_VACXIN": "Measles and Rubella Vaccine Live, Attenuated (Freeze-Dried)",
        "TEN_THUONG_MAI": "Measles and Rubella Vaccine Live, Attenuated (Freeze-Dried)",
        "COVID": 0
    },
    {
        "VACXIN_ID": 356,
        "TEN_VACXIN": "VAT (Lọ 20 liều)",
        "TEN_THUONG_MAI": "VAT (Lọ 20 liều)",
        "COVID": 0
    },
    {
        "VACXIN_ID": 357,
        "TEN_VACXIN": "Typhim Vi (Lọ 1 liều/0.5 ml)",
        "TEN_THUONG_MAI": "Typhim Vi (Lọ 1 liều/0.5 ml)",
        "COVID": 0
    },
    {
        "VACXIN_ID": 358,
        "TEN_VACXIN": "Hexaxim",
        "TEN_THUONG_MAI": "Hexaxim",
        "COVID": 0
    },
    {
        "VACXIN_ID": 359,
        "TEN_VACXIN": "Teatanus Antitoxin",
        "TEN_THUONG_MAI": "Teatanus Antitoxin",
        "COVID": 0
    },
    {
        "VACXIN_ID": 361,
        "TEN_VACXIN": "MMR II & Diluent inj 0.5ml",
        "TEN_THUONG_MAI": "MMR II & Diluent inj 0.5ml",
        "COVID": 0
    },
    {
        "VACXIN_ID": 362,
        "TEN_VACXIN": "Rotarix 1.5ml",
        "TEN_THUONG_MAI": "Rotarix 1.5ml",
        "COVID": 0
    },
    {
        "VACXIN_ID": 363,
        "TEN_VACXIN": "Varivax & Diluent Inj 0.5ml",
        "TEN_THUONG_MAI": "Varivax & Diluent Inj 0.5ml",
        "COVID": 0
    },
    {
        "VACXIN_ID": 364,
        "TEN_VACXIN": "Cervarix 0.5ml",
        "TEN_THUONG_MAI": "Cervarix 0.5ml",
        "COVID": 0
    },
    {
        "VACXIN_ID": 365,
        "TEN_VACXIN": "Jevax (Lọ 1 liều 0.5ml)",
        "TEN_THUONG_MAI": "Jevax (Lọ 1 liều 0.5ml)",
        "COVID": 0
    },
    {
        "VACXIN_ID": 366,
        "TEN_VACXIN": "Kháng huyết thanh viêm gan B Fovepta",
        "TEN_THUONG_MAI": "Kháng huyết thanh viêm gan B Fovepta",
        "COVID": 0
    },
    {
        "VACXIN_ID": 367,
        "TEN_VACXIN": "Measles, Mumps and Rubella Vaccine Live, Attenuated (Freeze-Dried) ",
        "TEN_THUONG_MAI": "Measles, Mumps and Rubella Vaccine Live, Attenuated (Freeze-Dried) ",
        "COVID": 0
    },
    {
        "VACXIN_ID": 368,
        "TEN_VACXIN": "Tresivac",
        "TEN_THUONG_MAI": "Tresivac",
        "COVID": 0
    },
    {
        "VACXIN_ID": 369,
        "TEN_VACXIN": "Mengo-BC",
        "TEN_THUONG_MAI": "Mengo-BC",
        "COVID": 0
    },
    {
        "VACXIN_ID": 370,
        "TEN_VACXIN": "Indirab",
        "TEN_THUONG_MAI": "Indirab",
        "COVID": 0
    },
    {
        "VACXIN_ID": 371,
        "TEN_VACXIN": "Speeda1",
        "TEN_THUONG_MAI": "Speeda1",
        "COVID": 0
    },
    {
        "VACXIN_ID": 372,
        "TEN_VACXIN": "ComBE Five",
        "TEN_THUONG_MAI": "ComBE Five",
        "COVID": 0
    },
    {
        "VACXIN_ID": 373,
        "TEN_VACXIN": "Influvac 2018/2019",
        "TEN_THUONG_MAI": "Influvac 2018/2019",
        "COVID": 0
    },
    {
        "VACXIN_ID": 374,
        "TEN_VACXIN": "Verorab 0.1ml",
        "TEN_THUONG_MAI": "Verorab 0.1ml",
        "COVID": 0
    },
    {
        "VACXIN_ID": 375,
        "TEN_VACXIN": "Abhayrab 0.1ml",
        "TEN_THUONG_MAI": "Abhayrab 0.1ml",
        "COVID": 0
    },
    {
        "VACXIN_ID": 376,
        "TEN_VACXIN": "DPT-VGB-HIB (SII)",
        "TEN_THUONG_MAI": "DPT-VGB-HIB (SII)",
        "COVID": 0
    },
    {
        "VACXIN_ID": 381,
        "TEN_VACXIN": "IVACFLU-S",
        "TEN_THUONG_MAI": "IVACFLU-S",
        "COVID": 0
    },
    {
        "VACXIN_ID": 382,
        "TEN_VACXIN": "Prevenar 13",
        "TEN_THUONG_MAI": "Prevenar 13",
        "COVID": 0
    },
    {
        "VACXIN_ID": 383,
        "TEN_VACXIN": "INFANRIX-IPV/Hib",
        "TEN_THUONG_MAI": "INFANRIX-IPV/Hib",
        "COVID": 0
    },
    {
        "VACXIN_ID": 384,
        "TEN_VACXIN": "Boostrix",
        "TEN_THUONG_MAI": "Boostrix",
        "COVID": 0
    },
    {
        "VACXIN_ID": 385,
        "TEN_VACXIN": "Immubron",
        "TEN_THUONG_MAI": "Immubron",
        "COVID": 0
    },
    {
        "VACXIN_ID": 386,
        "TEN_VACXIN": "Influvac 2020/2021",
        "TEN_THUONG_MAI": "Influvac 2020/2021",
        "COVID": 0
    },
    {
        "VACXIN_ID": 387,
        "TEN_VACXIN": "Influvac 2019/2020",
        "TEN_THUONG_MAI": "Influvac 2019/2020",
        "COVID": 0
    },
    {
        "VACXIN_ID": 388,
        "TEN_VACXIN": "Typhoid vi 0.5ml",
        "TEN_THUONG_MAI": "Typhoid vi 0.5ml",
        "COVID": 0
    },
    {
        "VACXIN_ID": 389,
        "TEN_VACXIN": "BCG-TCDV",
        "TEN_THUONG_MAI": "BCG-TCDV",
        "COVID": 0
    },
    {
        "VACXIN_ID": 390,
        "TEN_VACXIN": "Vinrab 1000 I.U",
        "TEN_THUONG_MAI": "Vinrab 1000 I.U",
        "COVID": 0
    },
    {
        "VACXIN_ID": 391,
        "TEN_VACXIN": "SPEEDA",
        "TEN_THUONG_MAI": "SPEEDA",
        "COVID": 0
    },
    {
        "VACXIN_ID": 392,
        "TEN_VACXIN": "INDIRAB 0.2 ml",
        "TEN_THUONG_MAI": "INDIRAB 0.2 ml",
        "COVID": 0
    },
    {
        "VACXIN_ID": 393,
        "TEN_VACXIN": "Abhayrab 0.2ml",
        "TEN_THUONG_MAI": "Abhayrab 0.2ml",
        "COVID": 0
    },
    {
        "VACXIN_ID": 394,
        "TEN_VACXIN": "Verorab 0.2ml",
        "TEN_THUONG_MAI": "Verorab 0.2ml",
        "COVID": 0
    },
    {
        "VACXIN_ID": 395,
        "TEN_VACXIN": "SAR 2ml",
        "TEN_THUONG_MAI": "SAR 2ml",
        "COVID": 0
    },
    {
        "VACXIN_ID": 397,
        "TEN_VACXIN": "JEEV 6mcg/0,5ml",
        "TEN_THUONG_MAI": "JEEV 6mcg/0,5ml",
        "COVID": 0
    },
    {
        "VACXIN_ID": 398,
        "TEN_VACXIN": "JEEV 3mcg/0,5ml",
        "TEN_THUONG_MAI": "JEEV 3mcg/0,5ml",
        "COVID": 0
    },
    {
        "VACXIN_ID": 478,
        "TEN_VACXIN": "Vaxigrip Tetra 0.5ml ",
        "TEN_THUONG_MAI": "Vaxigrip Tetra 0.5ml ",
        "COVID": 0
    },
    {
        "VACXIN_ID": 598,
        "TEN_VACXIN": "Influvac Tetra 2021/2022",
        "TEN_THUONG_MAI": "Influvac Tetra 2021/2022",
        "COVID": 0
    },
    {
        "VACXIN_ID": 618,
        "TEN_VACXIN": "GC FLU Quadrivalent pre-filled syringe inj",
        "TEN_THUONG_MAI": "GC FLU Quadrivalent pre-filled syringe inj",
        "COVID": 0
    },
    {
        "VACXIN_ID": 638,
        "TEN_VACXIN": "MRVAC",
        "TEN_THUONG_MAI": "MVVAC",
        "COVID": 0
    },
    {
        "VACXIN_ID": 658,
        "TEN_VACXIN": "Gardasil 9",
        "TEN_THUONG_MAI": "Gardasil 9",
        "COVID": 0
    },
    {
        "VACXIN_ID": 678,
        "TEN_VACXIN": "Influvac Tetra 2022/2023",
        "TEN_THUONG_MAI": "Influvac Tetra 2022/2023",
        "COVID": 0
    },
    {
        "VACXIN_ID": 738,
        "TEN_VACXIN": "Rotavin",
        "TEN_THUONG_MAI": "Rotavin",
        "COVID": 0
    },
    {
        "VACXIN_ID": 778,
        "TEN_VACXIN": "Influvac Tetra 2023/2024",
        "TEN_THUONG_MAI": "Influvax Tetra 2023/2024",
        "COVID": 0
    },
    {
        "VACXIN_ID": 818,
        "TEN_VACXIN": "DPT (Lọ 1 liều)",
        "TEN_THUONG_MAI": "DPT (Lọ 1 liều)",
        "COVID": None
    },
    {
        "VACXIN_ID": 838,
        "TEN_VACXIN": "Bexsero",
        "TEN_THUONG_MAI": "Bexsero",
        "COVID": 0
    },
    {
        "VACXIN_ID": 859,
        "TEN_VACXIN": "Pneumovax 23",
        "TEN_THUONG_MAI": "Pneumovax 23",
        "COVID": 0
    },
    {
        "VACXIN_ID": 878,
        "TEN_VACXIN": "Qdenga",
        "TEN_THUONG_MAI": "Qdenga",
        "COVID": 0
    },
    {
        "VACXIN_ID": 898,
        "TEN_VACXIN": "Shingrix",
        "TEN_THUONG_MAI": "Shingrix",
        "COVID": 0
    },
    {
        "VACXIN_ID": 918,
        "TEN_VACXIN": "Influvac Tetra 2024/2025",
        "TEN_THUONG_MAI": "Influvax Tetra 2024/2025",
        "COVID": 0
    },
    {
        "VACXIN_ID": 938,
        "TEN_VACXIN": "Rotarix - TCMR",
        "TEN_THUONG_MAI": "Rotarix",
        "COVID": 0
    },
    {
        "VACXIN_ID": 958,
        "TEN_VACXIN": "Influvac Tetra",
        "TEN_THUONG_MAI": "Influvax Tetra",
        "COVID": 0
    },
    {
        "VACXIN_ID": 978,
        "TEN_VACXIN": "Rotavin - TCMR",
        "TEN_THUONG_MAI": "Rotavin",
        "COVID": 0
    },
    {
        "VACXIN_ID": 998,
        "TEN_VACXIN": "IVACRIG",
        "TEN_THUONG_MAI": "IVACRIG",
        "COVID": 0
    },
    {
        "VACXIN_ID": 1018,
        "TEN_VACXIN": "ABRYSVO",
        "TEN_THUONG_MAI": "ABRYSVO",
        "COVID": 0
    },
    {
        "VACXIN_ID": 1038,
        "TEN_VACXIN": "Vaxneuvance",
        "TEN_THUONG_MAI": "Vaxneuvance",
        "COVID": 0
    },
    {
        "VACXIN_ID": 1058,
        "TEN_VACXIN": "Prevenar 20",
        "TEN_THUONG_MAI": "Prevenar 20",
        "COVID": 0
    },
    {
        "VACXIN_ID": 1078,
        "TEN_VACXIN": "MenQuadfi",
        "TEN_THUONG_MAI": "MenQuadfi",
        "COVID": 0
    },
    {
        "VACXIN_ID": 1098,
        "TEN_VACXIN": "Nimenrix",
        "TEN_THUONG_MAI": "Nimenrix",
        "COVID": 0
    },
    {
        "VACXIN_ID": 1118,
        "TEN_VACXIN": "ProQuad",
        "TEN_THUONG_MAI": "ProQuad",
        "COVID": 0
    },
    {
        "VACXIN_ID": 1138,
        "TEN_VACXIN": "Barycela inj",
        "TEN_THUONG_MAI": "Barycela inj",
        "COVID": 0
    },
    {
        "VACXIN_ID": 1158,
        "TEN_VACXIN": "Ivactuber",
        "TEN_THUONG_MAI": "Ivactuber",
        "COVID": 0
    }
]

VACCINE_LIST_JSON = get_vaccine_list()