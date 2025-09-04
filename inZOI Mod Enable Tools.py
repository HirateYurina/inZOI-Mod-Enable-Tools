import os
import json
import sys
import ctypes  # 用于调用系统API获取语言和设置窗口标题
from rich.console import Console
from rich.table import Table

# 中英文文本资源统一管理
TEXT_RESOURCES = {
    "zh": {
        "detecting_mods": "正在检测Mod开启情况...",
        "error_dir_not_found": "错误：未找到Mod目录",
        "confirm_dir_exists": "请确认inZOI/Mods文件夹是否存在于“Documents”目录下",
        "json_error": "JSON格式错误: {file_path}",
        "permission_error": "权限不足: {file_path}",
        "process_fail": "处理文件失败 {file_path}: {error_msg}",
        "table_header_index": "序号",
        "table_header_mod_name": "Mod名称",
        "table_header_status": "状态",
        "status_enabled": "已开启",
        "status_turned_on": "开启",
        "status_error": "错误",
        "status_warning": "警告",
        "status_error_detail": "错误: {error_msg}",
        "mod_unknown": "未知Mod ({dir_name})",
        "mod_format_error": "格式错误 ({dir_name})",
        "mod_permission_error": "权限不足 ({dir_name})",
        "mod_process_fail": "处理失败 ({dir_name})",
        "result_all_enabled": "共检测到 [green]{total}[/green] 个Mod，Mod均已开启，无需修改。",
        "result_modified": "共检测到 [green]{total}[/green] 个Mod，操作完成！本次共修改 [green]{modified}[/green] 个Mod。",
        "result_no_files": "未找到任何Mod配置文件",
        "result_no_modified": "操作完成！共修改 [green]{modified}[/green] 个mod配置文件。",
        "press_enter_close": "按回车键关闭窗口……",
        "program_error": "程序执行出错: {error_msg}",
        "console_title": "inZOI Mod 启用工具",
        "author_desc": "inZOI Mod 启用工具"
    },
    "en": {
        "detecting_mods": "Detecting Mod activation status...",
        "error_dir_not_found": "Error: Mod directory not found",
        "confirm_dir_exists": "Please confirm if the inZOI/Mods folder exists in the 'Documents' directory",
        "json_error": "JSON format error: {file_path}",
        "permission_error": "Permission denied: {file_path}",
        "process_fail": "Failed to process file {file_path}: {error_msg}",
        "table_header_index": "No.",
        "table_header_mod_name": "Mod Name",
        "table_header_status": "Status",
        "status_enabled": "Already Enabled",
        "status_turned_on": "Enabled",
        "status_error": "Error",
        "status_warning": "Warning",
        "status_error_detail": "Error: {error_msg}",
        "mod_unknown": "Unknown Mod ({dir_name})",
        "mod_format_error": "Format Error ({dir_name})",
        "mod_permission_error": "Permission Denied ({dir_name})",
        "mod_process_fail": "Process Failed ({dir_name})",
        "result_all_enabled": "Detected [green]{total}[/green] Mods in total, all Mods are already enabled, no modifications needed.",
        "result_modified": "Detected [green]{total}[/green] Mods in total, operation completed! Modified [green]{modified}[/green] Mods this time.",
        "result_no_files": "No Mod configuration files found",
        "result_no_modified": "Operation completed! Modified [green]{modified}[/green] Mod configuration files in total.",
        "press_enter_close": "Press Enter to close the window...",
        "program_error": "Program execution error: {error_msg}",
        "console_title": "inZOI Mod Enable Tools",
        "author_desc": "inZOI Mod Enable Tools"
    }
}

# 作者信息
AUTHOR_INFO = {
    "author": "JangFullmoon"
}

# 初始化控制台
console = Console()

def get_system_language():
    """
    获取Windows系统默认语言（修复版）
    返回值：'zh'（中文，含简繁所有区域）、'en'（其他语言）
    """
    try:
        # 1. 优先获取用户默认UI语言（最贴近系统显示语言）
        lang_id = ctypes.windll.kernel32.GetUserDefaultUILanguage()
        # 2. 提取主语言ID（LANGID结构：主语言占10位，子语言占6位）
        primary_lang = lang_id & 0x3FF  # 按位与操作获取低10位
        
        # 3. 完整中文主语言ID列表（覆盖简繁中文所有区域）
        # 修复：将字典语法{0x04: ...}改为集合语法{0x04, ...}，集合仅存值无需键值对
        chinese_primary_langs = {
            0x04  # 中文（主语言ID，所有中文区域统一为此值）
        }
        
        # 4. 判断是否为中文系统
        if primary_lang in chinese_primary_langs:
            return "zh"
        else:
            return "en"
    
    except Exception as e:
        # 语言检测失败时，优先尝试中文（提升中文用户体验）
        console.print(f"[yellow]系统语言检测警告: {str(e)}，默认使用中文显示[/yellow]")
        return "zh"

def set_console_title(title):
    """设置控制台窗口标题（仅Windows系统有效）"""
    if sys.platform.startswith('win32'):
        ctypes.windll.kernel32.SetConsoleTitleW(title)

def modify_mod_manifest():
    # 1. 获取系统语言并加载对应文本资源
    sys_lang = get_system_language()
    texts = TEXT_RESOURCES[sys_lang]
    
    try:        
        # 2. 拼接目标目录（Documents/inZOI/Mods）
        documents_path = os.path.expandvars('%USERPROFILE%\\Documents')
        target_dir = os.path.join(documents_path, 'inZOI', 'Mods')
        
        # 3. 显示检测提示
        console.print(f"[bold]{texts['detecting_mods']}[/bold]\n")
        
        # 4. 检查目录是否存在
        if not os.path.exists(target_dir):
            console.print(f"[red]{texts['error_dir_not_found']}[/red]")
            console.print(texts['confirm_dir_exists'])
            return

        results = []  # 存储(Mod名称, 状态, 状态样式)
        modified_count = 0

        # 5. 遍历目录处理Mod配置文件
        for root, dirs, files in os.walk(target_dir):
            for file in files:
                if file.lower() == 'mod_manifest.json':
                    file_path = os.path.join(root, file)
                    dir_name = os.path.basename(root)  # 当前Mod文件夹名
                    
                    try:
                        # 读取JSON配置
                        with open(file_path, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                        
                        # 获取Mod名称（优先用friendlyName，无则显示未知）
                        mod_name = data.get('friendlyName', texts['mod_unknown'].format(dir_name=dir_name))
                        
                        # 修改bEnable状态（False→True）
                        if data.get('bEnable') is False:
                            data['bEnable'] = True
                            with open(file_path, 'w', encoding='utf-8') as f:
                                json.dump(data, f, indent=4, ensure_ascii=False)
                            status = texts['status_turned_on']
                            status_style = "green"
                            modified_count += 1
                        else:
                            status = texts['status_enabled']
                            status_style = "green"

                    except json.JSONDecodeError:
                        # JSON格式错误
                        mod_name = texts['mod_format_error'].format(dir_name=dir_name)
                        status = texts['status_error']
                        status_style = "red"
                        console.print(f"[red]{texts['json_error'].format(file_path=file_path)}[/red]")
                    except PermissionError:
                        # 权限不足
                        mod_name = texts['mod_permission_error'].format(dir_name=dir_name)
                        status = texts['status_warning']
                        status_style = "yellow"
                        console.print(f"[yellow]{texts['permission_error'].format(file_path=file_path)}[/yellow]")
                    except Exception as e:
                        # 其他未知错误
                        mod_name = texts['mod_process_fail'].format(dir_name=dir_name)
                        status = texts['status_error_detail'].format(error_msg=str(e))
                        status_style = "red"
                        console.print(f"[red]{texts['process_fail'].format(file_path=file_path, error_msg=str(e))}[/red]")
                    
                    results.append([mod_name, status, status_style])

        # 6. 使用表格显示处理结果
        if results:
            table = Table(show_header=True, header_style="bold", border_style="default")
            table.add_column(texts['table_header_index'], width=6)
            table.add_column(texts['table_header_mod_name'])
            table.add_column(texts['table_header_status'])
            
            # 添加表格数据
            for i, (mod_name, status, style) in enumerate(results, 1):
                table.add_row(str(i), mod_name, f"[{style}]{status}[/{style}]")
            
            console.print(table)
            
            # 显示统计信息
            total_count = len(results)
            if modified_count == 0:
                console.print(f"[bold]{texts['result_all_enabled'].format(total=total_count)}[/bold]")
            else:
                console.print(f"[bold]{texts['result_modified'].format(total=total_count, modified=modified_count)}[/bold]")
        else:
            console.print(f"[yellow]{texts['result_no_files']}[/yellow]")
            console.print(f"[bold]{texts['result_no_modified'].format(modified=modified_count)}[/bold]")
        
        # 7. 显示作者信息和关闭提示
        author_desc = texts['author_desc']
        console.print(f"\n{author_desc} By: {AUTHOR_INFO['author']}\n\n{texts['press_enter_close']}")
        sys.stdin.read(1)
        
    except Exception as e:
        console.print(f"[red]{texts['program_error'].format(error_msg=str(e))}[/red]")
        sys.stdin.read(1)

if __name__ == "__main__":
    # 获取系统语言并设置窗口标题
    sys_lang = get_system_language()
    set_console_title(TEXT_RESOURCES[sys_lang]['console_title'])
    modify_mod_manifest()