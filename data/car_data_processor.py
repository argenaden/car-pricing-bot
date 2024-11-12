import os
import json

# (TODO) Move these to utils
YEAR_RANGE_START = 2018
YEAR_RANGE_END = 2024
KOR2ENG_MAP = {'현대': 'Hyundai', '기아': 'KIA', '제네시스': 'Genesis', '쉐보레': 'Chevrolet',
               '그랜저': 'Grandeur', '아반떼': 'Avante', '소나타': 'Sonata', '산타페': 'Santa Fe',
                '스타렉스': 'Starex', '투싼': 'Tucson', '카니발': 'Carnival', 'K5': 'K5', 'K7': 'K7',
                '쏘렌토': 'Sorento', '레이': 'Ray', '모닝': 'Morning', 'EQ900': 'EQ900', 'G70': 'G70',
                'G80': 'G80', 'G90': 'G90', 'GV70': 'GV70', 'GV80': 'GV80', 'GV90': 'GV90',
                '스파크': 'Spark', '말리부': 'Malibu', '트랙스': 'Trax', '크루즈': 'Cruze',
                '올란도': 'Orlando', '트레일블레이저': 'Trailblazer',
                '디젤': 'Дизель', '가솔린': 'Бензин', '가솔린+LPG': 'Бензин и газ', '수동': 'Механика', '자동': 'Автомат'}
ENG2RU_MAP = {'FRONT_DOOR_LEFT': 'левая передняя дверь', 'FRONT_DOOR_RIGHT': 'правая передняя дверь',
                'BACK_DOOR_LEFT': 'левая задняя дверь', 'BACK_DOOR_RIGHT': 'правая задняя дверь',
                'FRONT_FENDER_LEFT': 'левое переднее крыло', 'FRONT_FENDER_RIGHT': 'правое переднее крыло',
                'BACK_FENDER_LEFT': 'левое заднее крыло', 'BACK_FENDER_RIGHT': 'правое заднее крыло',
                'TRUNK_LID': 'крышка багажника', 'HOOD': 'капот'}


class CarDataProcessor:
    def __init__(self, data_path):
        self.data_path = data_path
        self.save_path = data_path.split('.')[0] + '_processed.json'
        self.raw_data = self.load_data(data_path)
        self.processed_data = {}
    
    def load_data(self, data_path):
        with open(data_path, 'r') as file:
            return json.load(file)
        print(f"Data loaded from {data_path}")
    def save_data(self, data, save_path):
        with open(save_path, 'w') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
        print(f"Processed data saved to {save_path}")
    
    def parse_main_data(self, main_dict):
        def parse_car_model(model):
            # model names are a bit confusing, 
            # the following trick is used as temporary solution
            for kor, eng in KOR2ENG_MAP.items():
                if kor in model:
                    return eng
            raise ValueError(f"Model {model} not found in the mapping.")
        
        def parse_price(price):
            # convert from 만원 to 원
            return int(float(price) * 10000)
        
        def parse_year(year):
            # convert year from 201253.0 to 2012
            year = int(year / 100)
            if year < YEAR_RANGE_START or year > YEAR_RANGE_END:
                raise ValueError(f"Year {year} is out of range.")
            return year

        if not main_dict:
            return {}

        manufacturer = KOR2ENG_MAP[main_dict['Manufacturer']]
        model = parse_car_model(main_dict['Model'])
        price = parse_price(main_dict['Price'])
        year = parse_year(main_dict['Year'])
        fuel = KOR2ENG_MAP[main_dict['FuelType']]
        mileage = int(main_dict['Mileage'])
        url = main_dict['URL']

        res = {
            'Manufacturer': manufacturer,
            'Model': model,
            'Price': price,
            'Year': year,
            'FuelType': fuel,
            'Mileage': mileage,
            'URL': url
        }
        return res
    
    def parse_profile_data(self, profile_dict):
        res = {}
        keys = ['myAccidentCnt', 'otherAccidentCnt', 'myAccidentCost', 'otherAccidentCost']
        if not profile_dict:
            for key in keys:
                res[key] = 0
            return res
        for key in keys:
            res[key] = profile_dict.get(key, 0)
        return res

    def parse_diagnosis_data(self, diagnosis_dict):
        res = {}
        if not diagnosis_dict:
            return res
        for item in diagnosis_dict['items']:
            if item['name'] in ['CHECKER_COMMENT', 'OUTER_PANEL_COMMENT']:
                res[item['name']] = item['result']
            else:
                res[item['name']] = item['resultCode']
        return res
    
    def parse_inspection_data(self, inspection_dict):
        res = {'inners': {}, 'outters': {}}
        if not inspection_dict:
            return res
        inners = {}
        for item in inspection_dict['inners']:
            info = {}
            for subitem in item['children']:
                try:
                    status = subitem['statusType']['title']
                except:
                    status = None
                info[subitem['type']['title']] = status
            inners[item['type']['title']] = info
        outers = {}
        for item in inspection_dict['outers']:
            outers[item['type']['title']] = item['statusTypes'][0]['title']
        res['inners'] = inners
        res['outters'] = outers
        return res

    def parse_description_data(self, description_dict):
        res = {}
        if not description_dict:
            return res
        key = 'contents'
        res[key] = description_dict[key]['text']
        return res
    
    def construct_asnwer_msg(self, car_info):
        answer_msg = f"*Марка:* {car_info['Manufacturer']}\n"
        answer_msg += f"*Модель:* {car_info['Model']}\n"
        answer_msg += f"*Год выпуска:* {car_info['Year']}\n"
        answer_msg += f"*Пробег:* {car_info['Mileage']} км\n"
        answer_msg += f"*Топливо:* {car_info['FuelType']}\n"
        answer_msg += f"*Цена:* {car_info['Price']} ₩\n"
        if car_info['myAccidentCnt'] == 0 and not car_info['replacement_parts']:
            short_answer_msg = answer_msg + f"*Состояние:* Отличное\n"
        else:
            short_answer_msg = answer_msg + f"*Состояние:* Присутствуют повреждения\n"
        answer_msg += f"*Количесто аварий:* {car_info['myAccidentCnt']}\n"
        answer_msg += f"*Страховая история\(ущерб нанесённый автомобилю\):* {car_info['myAccidentCost']} ₩\n"
        answer_msg += f"*Страховая история\(ущерб нанесённый другим автомобилям\):* {car_info['otherAccidentCost']} ₩\n"
        answer_msg += f"*Диагностика:* {car_info['diagnosis']}\n"
        answer_msg += f"[Cсылка на автомобиль]({car_info['URL']})\n"
        short_answer_msg += f"[Cсылка на автомобиль]({car_info['URL']})\n"
        car_info['short_answer_msg'] = short_answer_msg
        car_info['full_answer_msg'] = answer_msg

    def process_data(self):
        for key, value in self.raw_data.items():
            main_info = value['main']
            profile = value['profile']
            diagnosis = value['diagnosis']
            inspection = value['inspection']
            description = value['description']

            main_info = self.parse_main_data(main_info)
            accident = self.parse_profile_data(profile)
            diagnosis = self.parse_diagnosis_data(diagnosis)
            inspection = self.parse_inspection_data(inspection)
            description = self.parse_description_data(description)

            # Merge accident info into main_info
            main_info.update(accident)

            # Merge diagnosis info into main_info
            replaced_parts = []
            if diagnosis:
                chacker_comment = diagnosis.pop('CHECKER_COMMENT')
                outer_panel_comment = diagnosis.pop('OUTER_PANEL_COMMENT')
                for diag_key, diag_value in diagnosis.items():
                    if diag_value == 'NORMAL':
                        pass
                    elif diag_value == 'REPLACEMENT':
                        replaced_parts.append(ENG2RU_MAP[diag_key])
                    else:
                        raise NotImplementedError()
                if replaced_parts:
                    d_text = f"Официальная диагностика от Encar показала" \
                        f" что были заменены следующие детали: {', '.join(replaced_parts)}"
                else:
                    d_text = f"Официальная диагностика от Encar показала" \
                        " что автомобиль в отличном состоянии, без замененных деталей"
            else:
                d_text = "Информация об официальной диагностике от Encar отсутствует"
            main_info['diagnosis'] = d_text
            main_info['replacement_parts'] = replaced_parts

            # TODO: Merge inspection info into main_info
            # TODO: Merge description info into main_info

            self.construct_asnwer_msg(main_info)
            self.processed_data[key] = main_info
        
        self.save_data(self.processed_data, self.save_path)