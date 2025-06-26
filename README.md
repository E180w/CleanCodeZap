# CleanCodeZap ⚡

**CleanCodeZap** — это мощный CLI инструмент для автоматической очистки и оптимизации кода проектов на Python, JavaScript и Go. Инструмент удаляет неиспользуемые импорты, переменные, закомментированный код и автоматически форматирует код согласно стандартам языка.

![Tests](https://github.com/E180w/CleanCodeZap/workflows/Tests/badge.svg)
![Python](https://img.shields.io/badge/python-3.7+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## ✨ Возможности

- 🧹 **Удаление неиспользуемого кода**: Автоматически находит и удаляет неиспользуемые импорты, переменные и закомментированный код
- 📦 **Анализ зависимостей**: Проверяет `requirements.txt`, `package.json`, `go.mod` и находит неиспользуемые или устаревшие зависимости
- 🎨 **Автоматическое форматирование**: Использует `black` для Python, `prettier` для JavaScript, `gofmt` для Go
- 🔍 **Автоопределение языка**: Автоматически определяет язык проекта по файлам
- 💾 **Резервные копии**: Создает бэкапы перед внесением изменений
- 🌍 **Кроссплатформенность**: Работает на Windows, macOS и Linux
- 🚀 **Простота использования**: Интуитивный CLI интерфейс с понятными командами

## 📋 Поддерживаемые языки

| Язык | Расширения файлов | Инструменты форматирования | Файлы зависимостей |
|------|-------------------|----------------------------|-------------------|
| Python | `.py` | `black`, `autoflake` | `requirements.txt`, `setup.py`, `pyproject.toml` |
| JavaScript/TypeScript | `.js`, `.ts`, `.jsx`, `.tsx` | `prettier`, `eslint` | `package.json` |
| Go | `.go` | `gofmt`, `goimports` | `go.mod` |

## 🚀 Быстрый старт

### Установка Python (если не установлен)

<details>
<summary><strong>Windows</strong></summary>

1. Перейдите на [python.org](https://www.python.org/downloads/)
2. Скачайте последнюю версию Python (3.7 или выше)
3. Запустите установщик и **ОБЯЗАТЕЛЬНО** поставьте галочку "Add Python to PATH"
4. Перезагрузите компьютер
5. Откройте командную строку (Win+R, введите `cmd`) и проверьте установку:
   ```bash
   python --version
   pip --version
   ```

</details>

<details>
<summary><strong>macOS</strong></summary>

**Способ 1: Через официальный сайт**
1. Перейдите на [python.org](https://www.python.org/downloads/)
2. Скачайте последнюю версию Python для macOS
3. Установите скачанный пакет

**Способ 2: Через Homebrew (рекомендуется)**
1. Установите Homebrew, если не установлен:
   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```
2. Установите Python:
   ```bash
   brew install python
   ```

3. Проверьте установку:
   ```bash
   python3 --version
   pip3 --version
   ```

</details>

<details>
<summary><strong>Linux (Ubuntu/Debian)</strong></summary>

```bash
# Обновите пакеты
sudo apt update

# Установите Python и pip
sudo apt install python3 python3-pip

# Проверьте установку
python3 --version
pip3 --version
```

**Для других дистрибутивов:**
- **CentOS/RHEL/Fedora**: `sudo yum install python3 python3-pip` или `sudo dnf install python3 python3-pip`
- **Arch Linux**: `sudo pacman -S python python-pip`

</details>

### Установка CleanCodeZap

```bash
# Способ 1: Установка через pip (когда пакет будет опубликован)
pip install cleancodezap

# Способ 2: Установка из исходников
git clone https://github.com/E180w/CleanCodeZap.git
cd CleanCodeZap
pip install -e .
```

### Первый запуск

1. **Откройте терминал/командную строку**
   - Windows: Win+R → `cmd` → Enter
   - macOS: Cmd+Space → "Terminal" → Enter  
   - Linux: Ctrl+Alt+T

2. **Перейдите в папку с вашим проектом**
   ```bash
   cd путь/к/вашему/проекту
   ```

3. **Запустите анализ проекта**
   ```bash
   cleancodezap check
   ```

4. **Примените исправления**
   ```bash
   cleancodezap fix --backup
   ```

## 📖 Использование

### Основные команды

```bash
# Проверить проект на проблемы
cleancodezap check

# Исправить найденные проблемы
cleancodezap fix

# Форматировать код
cleancodezap format

# Анализировать зависимости  
cleancodezap deps

# Показать версию
cleancodezap --version

# Показать справку
cleancodezap --help
```

### Параметры командной строки

#### Общие параметры

| Параметр | Описание | Пример |
|----------|----------|---------|
| `--path`, `-p` | Путь к проекту | `cleancodezap check -p /path/to/project` |
| `--lang`, `-l` | Язык проекта | `cleancodezap check -l python` |

#### Команда `check`

```bash
cleancodezap check [OPTIONS]

# Примеры
cleancodezap check                           # Анализ текущей папки
cleancodezap check --path /home/user/project # Анализ конкретной папки
cleancodezap check --lang python             # Принудительно указать язык
cleancodezap check --dry-run                 # Показать без применения изменений
```

#### Команда `fix`

```bash
cleancodezap fix [OPTIONS]

# Примеры
cleancodezap fix                    # Исправить проблемы
cleancodezap fix --backup          # Создать резервную копию
cleancodezap fix --aggressive      # Агрессивная очистка
cleancodezap fix --backup --aggressive  # С бэкапом и агрессивно
```

#### Команда `format`

```bash
cleancodezap format [OPTIONS]

# Примеры
cleancodezap format                 # Форматировать код
cleancodezap format --lang python  # Форматировать как Python
```

#### Команда `deps`

```bash
cleancodezap deps [OPTIONS]

# Примеры
cleancodezap deps                   # Показать анализ зависимостей
cleancodezap deps --remove-unused  # Удалить неиспользуемые зависимости
```

## 💡 Примеры использования

### Пример 1: Очистка Python проекта

```bash
# Перейти в папку проекта
cd my_python_project

# Проверить что будет исправлено
cleancodezap check --lang python

# Создать бэкап и исправить проблемы
cleancodezap fix --backup --lang python

# Форматировать код по стандартам Python
cleancodezap format --lang python

# Проверить зависимости
cleancodezap deps --lang python
```

### Пример 2: Очистка JavaScript проекта

```bash
# Перейти в папку проекта
cd my_js_project

# Автоопределение языка и анализ
cleancodezap check

# Исправить с агрессивными настройками
cleancodezap fix --aggressive --backup

# Удалить неиспользуемые зависимости
cleancodezap deps --remove-unused
```

### Пример 3: Полная очистка проекта

```bash
# Комплексная очистка проекта
cleancodezap check                    # 1. Анализ
cleancodezap fix --backup           # 2. Исправления с бэкапом  
cleancodezap format                  # 3. Форматирование
cleancodezap deps --remove-unused   # 4. Очистка зависимостей
```

## 🔧 Настройки по языкам

### Python

CleanCodeZap использует следующие инструменты для Python:

- **autoflake**: Удаление неиспользуемых импортов и переменных
- **black**: Форматирование кода
- **Анализ**: `requirements.txt`, `setup.py`, `pyproject.toml`

```bash
# Установка дополнительных инструментов для Python (опционально)
pip install autoflake black

# Использование
cleancodezap fix --lang python --aggressive
```

### JavaScript/TypeScript

Для JavaScript проектов используются:

- **ESLint**: Поиск и исправление проблем
- **Prettier**: Форматирование кода
- **Анализ**: `package.json`

```bash
# Установка инструментов для JS (опционально)
npm install -g eslint prettier

# Использование
cleancodezap fix --lang javascript
```

### Go

Для Go проектов:

- **gofmt**: Форматирование
- **goimports**: Управление импортами
- **go mod tidy**: Очистка зависимостей

```bash
# Инструменты Go обычно идут с установкой Go
go install golang.org/x/tools/cmd/goimports@latest

# Использование
cleancodezap fix --lang go
```

## 🛠️ Установка для разработки

```bash
# Клонирование репозитория
git clone https://github.com/E180w/CleanCodeZap.git
cd CleanCodeZap

# Создание виртуального окружения
python -m venv venv

# Активация виртуального окружения
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Установка зависимостей для разработки
pip install -e ".[dev]"

# Запуск тестов
pytest
```

## 🐛 Решение проблем

### Часто встречающиеся ошибки

<details>
<summary><strong>"python: command not found" или "'cleancodezap' is not recognized"</strong></summary>

**Проблема**: Python не установлен или не добавлен в PATH.

**Решение**:
1. Переустановите Python с официального сайта
2. При установке обязательно поставьте галочку "Add Python to PATH"
3. Перезагрузите компьютер
4. Проверьте: `python --version`

</details>

<details>
<summary><strong>"No project files found, check the path"</strong></summary>

**Проблема**: CleanCodeZap не может найти файлы поддерживаемых языков.

**Решение**:
1. Убедитесь, что вы в правильной папке: `pwd` (Linux/macOS) или `cd` (Windows)
2. Проверьте, есть ли файлы `.py`, `.js`, `.go` в проекте
3. Укажите путь явно: `cleancodezap check --path /path/to/project`
4. Укажите язык явно: `cleancodezap check --lang python`

</details>

<details>
<summary><strong>"Permission denied" или ошибки доступа</strong></summary>

**Проблема**: Нет прав на изменение файлов.

**Решение**:
- **Linux/macOS**: Попробуйте `sudo cleancodezap fix` (осторожно!)
- **Windows**: Запустите командную строку от имени администратора
- Или измените права на папку проекта

</details>

<details>
<summary><strong>Ошибки установки пакетов</strong></summary>

**Проблема**: Не удается установить CleanCodeZap или зависимости.

**Решение**:
```bash
# Обновите pip
python -m pip install --upgrade pip

# Установите заново
pip install --force-reinstall cleancodezap

# Или с правами администратора (если нужно)
pip install --user cleancodezap
```

</details>

### Получение помощи

1. **Проверьте версию**: `cleancodezap --version`
2. **Посмотрите справку**: `cleancodezap --help` 
3. **Создайте issue**: [GitHub Issues](https://github.com/E180w/CleanCodeZap/issues)
4. **Включите отладочную информацию** при создании issue:
   ```bash
   cleancodezap check --path . --lang python > debug.log 2>&1
   ```

## 📚 Дополнительные ресурсы

### Обучающие материалы

- [Официальная документация Python](https://docs.python.org/3/)
- [Руководство по работе с командной строкой](https://tutorial.djangogirls.org/ru/intro_to_command_line/)
- [Основы Git и GitHub](https://guides.github.com/activities/hello-world/)

### Инструменты разработки

- [Visual Studio Code](https://code.visualstudio.com/) - рекомендуемый редактор
- [PyCharm](https://www.jetbrains.com/pycharm/) - IDE для Python
- [Git](https://git-scm.com/) - система контроля версий

## 🤝 Вклад в проект

Мы приветствуем вклад в развитие CleanCodeZap! 

### Как внести вклад

1. **Fork** репозитория
2. **Создайте** ветку для функции: `git checkout -b feature/AmazingFeature`
3. **Внесите** изменения и добавьте тесты
4. **Убедитесь**, что тесты проходят: `pytest`
5. **Commit** изменения: `git commit -m 'Add some AmazingFeature'`
6. **Push** в ветку: `git push origin feature/AmazingFeature`
7. **Создайте** Pull Request

### Рекомендации

- Следуйте стилю кода проекта
- Добавляйте тесты для новой функциональности
- Обновляйте документацию при необходимости
- Используйте понятные commit сообщения

## 📄 Лицензия

Этот проект распространяется под лицензией MIT. Смотрите файл [LICENSE](LICENSE) для деталей.

## 📞 Контакты

- **GitHub**: [https://github.com/E180w/CleanCodeZap](https://github.com/E180w/CleanCodeZap)
- **Issues**: [https://github.com/E180w/CleanCodeZap/issues](https://github.com/E180w/CleanCodeZap/issues)
- **Email**: team@cleancodezap.com

## 🏆 Благодарности

- [click](https://click.palletsprojects.com/) - За отличную библиотеку CLI
- [autoflake](https://github.com/PyCQA/autoflake) - За инструменты очистки Python кода
- [black](https://black.readthedocs.io/) - За безупречное форматирование Python
- Всем участникам open-source сообщества!

---

**CleanCodeZap** - сделайте ваш код чище за секунды! ⚡ 