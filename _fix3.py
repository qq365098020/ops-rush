with open('/home/oiio/橙子的工作台/运营RUSH/index.html', 'r') as f:
    src = f.read()

# 1. Rename
src = src.replace("每旬查库&改密码',type:'旬'", "每旬查库&改密码&登记',type:'旬'")

# 2. Fix quickDone: for 旬 tasks, don't bail out on status=='done'
old_qd = "if(s.status==='done'){this.openDetail(taskId);return}\n    this.completeTask(taskId, TODAY());if(document.getElementById('detailModal').classList.contains('show'))this.refreshDetail(taskId);"
new_qd = "if(s.status==='done'&&task.type!=='旬'){this.openDetail(taskId);return}\n    this.completeTask(taskId, TODAY());if(document.getElementById('detailModal').classList.contains('show'))this.refreshDetail(taskId);"
src = src.replace(old_qd, new_qd)

# 3. Fix renderDashboard: 旬 completed → 进行中 (not 待处理)
old_route = "if(s.status==='done'&&task.multiCompletion&&!this.isMonthFullyComplete(task))overdue.push(task);"
new_route = "if(s.status==='done'&&task.multiCompletion&&!this.isMonthFullyComplete(task)){if(task.type==='旬')upcoming.push(task);else overdue.push(task)}"
src = src.replace(old_route, new_route)

# Verify
import re
for item in ['每旬查库&改密码&登记', "task.type!=='旬'", '旬\')upcoming.push']:
    if re.search(item, src):
        print('  '+item+': OK')

o = src.count('{')
c = src.count('}')
print('Braces: {'+str(o)+' }'+str(c)+(' OK' if o==c else ' FAIL'))

with open('/home/oiio/橙子的工作台/运营RUSH/index.html', 'w') as f:
    f.write(src)
print('Done!')
