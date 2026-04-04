from pathlib import Path


def build_status_explanation(state: dict) -> str:
    status = state.get('status') or 'unknown'
    mapping = {
        'created': '刚创建，等待你填写需求',
        'initialized': '已初始化，可以开始提需求',
        'analyzing': '正在分析需求，请稍等...',
        'pending_confirm': '方案已生成，等你确认',
        'confirmed': '方案已确认，准备生成代码',
        'writing': '正在生成代码...',
        'written': '代码已生成，正在审查中',
        'reviewing': '正在审查代码...',
        'review_passed': '审查通过！',
        'needs_fix': '审查发现问题，正在修复',
        'fixing': '正在修复问题...',
        'deploying': '正在部署...',
        'sealed': '已封版归档',
        'failed': '上次操作出了点问题',
    }
    return mapping.get(status, '状态未知')


def build_next_step_hint(state: dict) -> str:
    status = state.get('status') or 'unknown'
    mapping = {
        'created': '运行 dtflow start --idea "你的需求" 来开始',
        'initialized': '运行 dtflow start --idea "你的需求" 来开始',
        'pending_confirm': '运行 dtflow start --confirm 确认方案，或 --feedback "意见" 提出调整',
        'confirmed': '运行 dtflow start 继续（会先预览代码）',
        'written': '系统正在自动审查',
        'review_passed': '运行 dtflow start --deploy 部署上线',
        'needs_fix': '运行 dtflow start 自动修复',
        'failed': '运行 dtflow advanced status 查看详情',
        'sealed': '版本已结束，运行 dtflow start --idea "新需求" 开始新版本',
    }
    return mapping.get(status, '运行 dtflow start 继续')
