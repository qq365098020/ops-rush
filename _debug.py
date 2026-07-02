with open('/home/oiio/橙子的工作台/运营RUSH/index.html', 'r', encoding='utf-8') as f:
    src = f.read()

# Add try/catch wrapper to openDetail
old1 = "  openDetail(taskId){\n    const task=this.tasks.find(t=>t.id===taskId);if(!task)return;\n    const now=new Date();this._miniCalMonth=now.getMonth();this._miniCalYear=now.getFullYear();\n    const s=this.getTaskStatus(task);\n    let html=`<div class=\"modal-title\">"
new1 = "  openDetail(taskId){\n    try{\n    const task=this.tasks.find(t=>t.id===taskId);if(!task){this.toast('no task: '+taskId);return;}\n    const now=new Date();this._miniCalMonth=now.getMonth();this._miniCalYear=now.getFullYear();\n    const s=this.getTaskStatus(task);\n    let html=`<div class=\"modal-title\">"
assert old1 in src, "openDetail start not found"
src = src.replace(old1, new1)

old2 = "    document.getElementById('detailContent').innerHTML=html;\n    document.getElementById('detailModal').classList.add('show');\n  }"
new2 = "    document.getElementById('detailContent').innerHTML=html;\n    document.getElementById('detailModal').classList.add('show');\n    }catch(e){this.toast('ERR: '+e.message)}\n  }"
assert old2 in src, "openDetail end not found"
src = src.replace(old2, new2)

with open('/home/oiio/橙子的工作台/运营RUSH/index.html', 'w', encoding='utf-8') as f:
    f.write(src)

o = src.count('{')
c = src.count('}')
print('Total: {' + str(o) + ' }' + str(c) + ' diff=' + str(o-c))
print('Done')
