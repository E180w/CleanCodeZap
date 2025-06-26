#!/usr/bin/env python3
"""
CleanCodeZap CLI - Main command line interface.
"""

import os
import sys
import click
from pathlib import Path
from typing import Optional

from .core import CodeCleaner
from .utils import (
    detect_project_language, 
    validate_project_path,
    print_success,
    print_error,
    print_info,
    print_warning
)


@click.group(invoke_without_command=True)
@click.option('--version', is_flag=True, help='Show version information')
@click.pass_context
def cli(ctx, version):
    """
    CleanCodeZap - Инструмент для очистки и оптимизации кода.
    
    Поддерживает Python, JavaScript и Go проекты.
    Удаляет неиспользуемые импорты, переменные и закомментированный код.
    """
    if version:
        from . import __version__
        click.echo(f"CleanCodeZap версия {__version__}")
        return
    
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@cli.command()
@click.option('--path', '-p', default='.', help='Путь к проекту (по умолчанию: текущая директория)')
@click.option('--lang', '-l', type=click.Choice(['python', 'javascript', 'go', 'auto']), 
              default='auto', help='Язык проекта (по умолчанию: автоопределение)')
@click.option('--dry-run', is_flag=True, help='Показать изменения без их применения')
def check(path, lang, dry_run):
    """
    Проверяет проект и показывает, что будет очищено.
    """
    try:
        project_path = Path(path).resolve()
        if not validate_project_path(project_path):
            print_error(f"Путь не найден или недоступен: {project_path}")
            sys.exit(1)
        
        if lang == 'auto':
            detected_lang = detect_project_language(project_path)
            if not detected_lang:
                print_error("Не удалось определить язык проекта. Попробуйте указать --lang явно.")
                sys.exit(1)
            lang = detected_lang
            print_info(f"Автоматически определен язык: {lang}")
        
        cleaner = CodeCleaner(project_path, lang)
        
        print_info(f"Анализ проекта: {project_path}")
        print_info(f"Язык: {lang}")
        
        issues = cleaner.analyze()
        
        if not issues:
            print_success("✅ Проект уже оптимизирован! Проблем не найдено.")
            return
        
        print_warning(f"Найдено проблем: {len(issues)}")
        for issue in issues:
            click.echo(f"  - {issue}")
        
        if dry_run:
            print_info("Режим dry-run: изменения не применены")
        else:
            print_info("Для применения изменений используйте: cleancodezap fix")
            
    except Exception as e:
        print_error(f"Ошибка при анализе: {str(e)}")
        sys.exit(1)


@cli.command()
@click.option('--path', '-p', default='.', help='Путь к проекту (по умолчанию: текущая директория)')
@click.option('--lang', '-l', type=click.Choice(['python', 'javascript', 'go', 'auto']), 
              default='auto', help='Язык проекта (по умолчанию: автоопределение)')
@click.option('--backup', is_flag=True, help='Создать резервную копию перед изменениями')
@click.option('--aggressive', is_flag=True, help='Агрессивная очистка (может потребовать проверки)')
def fix(path, lang, backup, aggressive):
    """
    Исправляет найденные проблемы в проекте.
    """
    try:
        project_path = Path(path).resolve()
        if not validate_project_path(project_path):
            print_error(f"Путь не найден или недоступен: {project_path}")
            sys.exit(1)
        
        if lang == 'auto':
            detected_lang = detect_project_language(project_path)
            if not detected_lang:
                print_error("Не удалось определить язык проекта. Попробуйте указать --lang явно.")
                sys.exit(1)
            lang = detected_lang
            print_info(f"Автоматически определен язык: {lang}")
        
        cleaner = CodeCleaner(project_path, lang)
        
        print_info(f"Оптимизация проекта: {project_path}")
        print_info(f"Язык: {lang}")
        
        if backup:
            backup_path = cleaner.create_backup()
            print_info(f"Создана резервная копия: {backup_path}")
        
        results = cleaner.clean(aggressive=aggressive)
        
        if results['files_processed'] == 0:
            print_success("✅ Проект уже оптимизирован!")
            return
        
        print_success(f"✅ Оптимизация завершена!")
        print_info(f"Обработано файлов: {results['files_processed']}")
        print_info(f"Удалено неиспользуемых импортов: {results['unused_imports_removed']}")
        print_info(f"Удалено неиспользуемых переменных: {results['unused_variables_removed']}")
        print_info(f"Удалено комментариев: {results['comments_removed']}")
        
        if results['dependencies_cleaned']:
            print_info(f"Очищено зависимостей: {results['dependencies_cleaned']}")
            
    except Exception as e:
        print_error(f"Ошибка при оптимизации: {str(e)}")
        sys.exit(1)


@cli.command()
@click.option('--path', '-p', default='.', help='Путь к проекту (по умолчанию: текущая директория)')
@click.option('--lang', '-l', type=click.Choice(['python', 'javascript', 'go', 'auto']), 
              default='auto', help='Язык проекта (по умолчанию: автоопределение)')
def format(path, lang):
    """
    Форматирует код проекта согласно стандартам языка.
    """
    try:
        project_path = Path(path).resolve()
        if not validate_project_path(project_path):
            print_error(f"Путь не найден или недоступен: {project_path}")
            sys.exit(1)
        
        if lang == 'auto':
            detected_lang = detect_project_language(project_path)
            if not detected_lang:
                print_error("Не удалось определить язык проекта. Попробуйте указать --lang явно.")
                sys.exit(1)
            lang = detected_lang
            print_info(f"Автоматически определен язык: {lang}")
        
        cleaner = CodeCleaner(project_path, lang)
        
        print_info(f"Форматирование проекта: {project_path}")
        print_info(f"Язык: {lang}")
        
        results = cleaner.format_code()
        
        if results['files_formatted'] == 0:
            print_success("✅ Код уже правильно отформатирован!")
            return
        
        print_success(f"✅ Форматирование завершено!")
        print_info(f"Отформатировано файлов: {results['files_formatted']}")
            
    except Exception as e:
        print_error(f"Ошибка при форматировании: {str(e)}")
        sys.exit(1)


@cli.command()
@click.option('--path', '-p', default='.', help='Путь к проекту (по умолчанию: текущая директория)')
@click.option('--lang', '-l', type=click.Choice(['python', 'javascript', 'go', 'auto']), 
              default='auto', help='Язык проекта (по умолчанию: автоопределение)')
@click.option('--remove-unused', is_flag=True, help='Удалить неиспользуемые зависимости')
def deps(path, lang, remove_unused):
    """
    Анализирует зависимости проекта и показывает неиспользуемые/устаревшие.
    """
    try:
        project_path = Path(path).resolve()
        if not validate_project_path(project_path):
            print_error(f"Путь не найден или недоступен: {project_path}")
            sys.exit(1)
        
        if lang == 'auto':
            detected_lang = detect_project_language(project_path)
            if not detected_lang:
                print_error("Не удалось определить язык проекта. Попробуйте указать --lang явно.")
                sys.exit(1)
            lang = detected_lang
            print_info(f"Автоматически определен язык: {lang}")
        
        cleaner = CodeCleaner(project_path, lang)
        
        print_info(f"Анализ зависимостей: {project_path}")
        print_info(f"Язык: {lang}")
        
        results = cleaner.analyze_dependencies(remove_unused=remove_unused)
        
        if not results['unused_dependencies'] and not results['outdated_dependencies']:
            print_success("✅ Все зависимости актуальны и используются!")
            return
        
        if results['unused_dependencies']:
            print_warning(f"Неиспользуемые зависимости ({len(results['unused_dependencies'])}):")
            for dep in results['unused_dependencies']:
                click.echo(f"  - {dep}")
        
        if results['outdated_dependencies']:
            print_warning(f"Устаревшие зависимости ({len(results['outdated_dependencies'])}):")
            for dep, version in results['outdated_dependencies'].items():
                click.echo(f"  - {dep}: {version['current']} → {version['latest']}")
        
        if remove_unused and results['unused_dependencies']:
            print_success(f"✅ Удалено неиспользуемых зависимостей: {len(results['unused_dependencies'])}")
        elif results['unused_dependencies']:
            print_info("Для удаления неиспользуемых зависимостей используйте: cleancodezap deps --remove-unused")
            
    except Exception as e:
        print_error(f"Ошибка при анализе зависимостей: {str(e)}")
        sys.exit(1)


def main():
    """Main entry point for the CLI."""
    try:
        cli()
    except KeyboardInterrupt:
        print_error("\nОперация прервана пользователем")
        sys.exit(1)
    except Exception as e:
        print_error(f"Неожиданная ошибка: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    main() 