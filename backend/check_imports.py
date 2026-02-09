"""
检查所有模块导入是否正常
"""
import sys
import traceback

def check_imports():
    """检查所有必要的导入"""
    errors = []
    
    print("=" * 50)
    print("检查模块导入...")
    print("=" * 50)
    
    modules_to_check = [
        ("fastapi", "FastAPI"),
        ("uvicorn", "uvicorn"),
        ("sqlalchemy", "SQLAlchemy"),
        ("pymysql", "PyMySQL"),
        ("apscheduler", "APScheduler"),
        ("requests", "requests"),
        ("bs4", "BeautifulSoup"),
        ("pydantic", "Pydantic"),
        ("pydantic_settings", "Pydantic Settings"),
    ]
    
    print("\n检查第三方库...")
    for module_name, display_name in modules_to_check:
        try:
            __import__(module_name)
            print(f"  ✓ {display_name}")
        except ImportError as e:
            print(f"  ✗ {display_name} - 未安装")
            errors.append(f"{display_name}: {e}")
    
    print("\n检查项目模块...")
    project_modules = [
        "app.config",
        "app.database",
        "app.models",
        "app.schemas",
        "app.crawler",
        "app.alert",
        "app.services",
        "app.scheduler",
        "app.api",
        "app.api.power",
        "app.api.alert",
        "app.api.system",
        "app.main",
    ]
    
    for module_name in project_modules:
        try:
            __import__(module_name)
            print(f"  ✓ {module_name}")
        except Exception as e:
            print(f"  ✗ {module_name}")
            errors.append(f"{module_name}: {e}")
            traceback.print_exc()
    
    print("\n" + "=" * 50)
    if errors:
        print("发现以下错误：")
        for error in errors:
            print(f"  - {error}")
        print("\n请运行以下命令安装依赖：")
        print("  pip install -r requirements.txt")
        return False
    else:
        print("✓ 所有模块导入正常！")
        return True

if __name__ == "__main__":
    success = check_imports()
    sys.exit(0 if success else 1)
