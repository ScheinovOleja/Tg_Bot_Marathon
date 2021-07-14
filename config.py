INTENTS = [
    {
        "name": "Регистрация",
        "tokens": ["start", "register"],
        "scenario": "register",
        "answer": ""
    },
    {
        "name": "Замеры ДО",
        "tokens": ["measurement_before"],
        "scenario": "measurement_before",
        "answer": ""
    },
    {
        "name": "Замеры ПОСЛЕ",
        "tokens": ["measurement_after"],
        "scenario": "measurement_after",
        "answer": ""
    },
    {
        "name": "Рассчитать ККАЛ",
        "tokens": ["calculate_kcal"],
        "scenario": "calculate_kcal",
        "answer": ""
    }
]

SCENARIOS = {
    "register": {
        "first_step": "step1",
        "steps": {
            "step1":
                {
                    "text": "Доброго времени суток!\n"
                            "Прошу заполнять данные верно, так как в дальнейшем они будут использоваться для подсчета "
                            "данных!\n"
                            "Как вас зовут?(Напишите ваши Фамилию и Имя через пробел)\n❗️ "
                            "Например: Иванова Мария",
                    "failure_text": "Что-то пошло не так. "
                                    "Повторите попытку!(Напишите ваши Фамилию и Имя через пробел)\n❗️ Например: "
                                    "Иванова Мария",
                    "handler": "name_handler",
                    "next_step": "step2"
                },
            "step2":
                {
                    "text": "Выберите ваш пол:",
                    "failure_text": 'Не нужно писать, просто нажмите на кнопку!',
                    "handler": "sex_handler",
                    "next_step": "step3"
                },
            "step3":
                {
                    "text": "Введите дату своего рождения в формате ДД.ММ.ГГГГ\n❗️ Например: 29.08.1995",
                    "failure_text": "Вы ввели некорректную дату рождения. Повторите попытку!\n❗️ Например: 29.08.1995",
                    "handler": "birthday_handler",
                    "next_step": "step4",
                },
            "step4":
                {
                    "text": "Привет {name}!\nВыберите пункт меню:",
                    "failure_text": None,
                    "handler": None,
                    "next_step": None,
                }
        }
    },
    "measurement_before": {
        "first_step": "step1",
        "steps": {
            "step1":
                {
                    "text": "Введите обхват груди в см (этап марафона ДО):\n❗️ Например: 84",
                    "failure_text": "Что-то пошло не так. Повторите попытку!\n"
                                    "Введите обхват груди в см:\n❗️ Например: 84",
                    "handler": "breast_handler_before",
                    "next_step": "step2"

                },
            "step2":
                {
                    "text": "Введите обхват талии в см (этап марафона ДО):\n❗️ Например: 63",
                    "failure_text": "Что-то пошло не так. Повторите попытку!\n"
                                    "Введите обхват талии в см:\n❗️ Например: 63",
                    "handler": "waist_handler_before",
                    "next_step": "step3"
                },
            "step3":
                {
                    "text": "Введите обхват бедер в см (этап марафона ДО):\n❗️ Например: 96",
                    "failure_text": "Что-то пошло не так. Повторите попытку!\n"
                                    "Введите обхват бедер в см:\n❗️ Например: 96",
                    "handler": "femur_handler_before",
                    "next_step": "step4",
                },
            "step4":
                {
                    "text": "Введите ваш вес в кг (этап марафона ДО):\n❗️ Например: 57",
                    "failure_text": "Что-то пошло не так. Повторите попытку!\nВведите ваш вес в кг:\n❗️ Например: 57",
                    "handler": "weight_handler_before",
                    "next_step": "step5",
                },
            "step5":
                {
                    "text": "Ваши данные успешно введены! Спасибо за предоставленную информацию!",
                    "failure_text": None,
                    "handler": None,
                    "next_step": None,
                }
        }
    },
    "measurement_after": {
        "first_step": "step1",
        "steps": {
            "step1":
                {
                    "text": "Введите обхват груди в см (этап марафона ПОСЛЕ):\n❗️ Например: 84",
                    "failure_text": "Что-то пошло не так. Повторите попытку!\n"
                                    "Введите обхват груди в см:\n❗️ Например: 84",
                    "handler": "breast_handler_after",
                    "next_step": "step2"

                },
            "step2":
                {
                    "text": "Введите обхват талии в см (этап марафона ПОСЛЕ):\n❗️ Например: 63",
                    "failure_text": "Что-то пошло не так. Повторите попытку!\n"
                                    "Введите обхват талии в см:\n❗️ Например: 63",
                    "handler": "waist_handler_after",
                    "next_step": "step3"
                },
            "step3":
                {
                    "text": "Введите обхват бедер в см (этап марафона ПОСЛЕ):\n❗️ Например: 96",
                    "failure_text": "Что-то пошло не так. Повторите попытку!\n"
                                    "Введите обхват бедер в см:\n❗️ Например: 96",
                    "handler": "femur_handler_after",
                    "next_step": "step4",
                },
            "step4":
                {
                    "text": "Введите ваш вес в кг (этап марафона ПОСЛЕ):\n❗️ Например: 57",
                    "failure_text": "Что-то пошло не так. Повторите попытку!\n"
                                    "Введите ваш вес в кг:\n❗️ Например: 57",
                    "handler": "weight_handler_after",
                    "next_step": "step5",
                },
            "step5":
                {
                    "text": "Ваши данные успешно введены! Спасибо за предоставленную информацию!",
                    "failure_text": None,
                    "handler": None,
                    "next_step": None,
                }
        }
    },
    "calculate_kcal": {
        "first_step": "step1",
        "steps": {
            "step1":
                {
                    "text": "Введите ваш вес на данный момент (в кг):\n❗️ Например: 57",
                    "failure_text": "Что-то пошло не так. Повторите попытку!\n"
                                    "Введите ваш вес на данный момент(в кг):\n❗️ Например: 57",
                    "handler": "calculate_weight_handler",
                    "next_step": "step2"

                },
            "step2":
                {
                    "text": "Введите ваш рост в данный момент (в см):\n❗️ Например: 164",
                    "failure_text": "Что-то пошло не так. Повторите попытку!\n"
                                    "Введите ваш рост в данный момент (в см):\n❗️ Например: 164",
                    "handler": "calculate_height_handler",
                    "next_step": "step3"
                },
            "step3":
                {
                    "text": "Сколько раз в неделю вы занимаетесь спортом?\n"
                            "Выберите из предложенных вариантов! Только честно 😉:",
                    "failure_text": "Что-то пошло не так. Повторите попытку!",
                    "handler": 'calculate_activity',
                    "next_step": "step4",
                },
            "step4":
                {
                    "text": None,
                    "failure_text": None,
                    "handler": None,
                    "next_step": None,
                }
        }
    }
}
