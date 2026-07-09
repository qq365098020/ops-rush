with open('/home/oiio/橙子的工作台/运营RUSH/index.html', 'r') as f:
    src = f.read()

# === Change 1: Remove cash_zero from DEFAULT_TASKS ===
old_cash = "  {id:'cash_zero',name:'现金登记为0',type:'rolling',severity:'green',intervalDays:1,postponeSat:true,lastCompleted:null,reviews:[],note:'',completionHistory:[],typeLabel:'每日 · 1次（跳过周六）',desc:'每天完成一次现金登记归零。周六关门日跳过。'},\n  "
assert old_cash in src, "cash_zero DEFAULT_TASKS not found!"
src = src.replace(old_cash, "  ")
print("Removed cash_zero from DEFAULT_TASKS")

# === Change 2: Remove cash_zero from migration ===
# Remove the rolling postponeSat logic for cash_zero
# Check if there's migration code that references cash_zero
if 'cash_zero' in src:
    # Find and remove the postponeSat rolling logic
    old_migrate = "if(t.id==='atm_cleaning'){t.desc=''}if(t.id==='computer_log'){t.type='monthly_multi';t.days=[2,17];t.multiCompletion=true;if(!t.completions)t.completions={};delete t.weekday;delete t.monthlyTarget}"
    assert old_migrate in src, "migration not found!"
    print("Migration found OK")

# === Change 3: Find renderCard and modify it ===
# The current renderCard at line 977 builds card HTML
# We need to replace the card-meta div with new layout

old_card_meta = '<div class="card-meta"><div class="card-due">${s.dueDate?(task.type===\'rolling\'?\'下次 \'+fmtDateShort(s.dueDate):\'截止 \'+fmtDateShort(s.dueDate)):(s.label||\'\')}</div><div class="card-countdown ${cc}">${s.label}</div></div>'

new_card_meta = '<div class="card-meta"><div class="card-countdown ${cc}">${cdText}</div></div>'

# Find where renderCard function body builds the return string
# We need to replace the card-top + card-meta section

old_card_html = '''    return`<div class="task-card ${sevClass} ${overdue?'overdue':''} ${doneClass}">
      <div class="card-body" onclick="app.openDetail('${task.id}')">
        <div class="card-top"><div class="card-name">${task.name}</div></div>
        <div class="card-meta"><div class="card-due">${s.dueDate?(task.type==='rolling'?'下次 '+fmtDateShort(s.dueDate):'截止 '+fmtDateShort(s.dueDate)):(s.label||'')}</div><div class="card-countdown ${cc}">${s.label}</div></div>
      </div>
      <div class="card-cal-btn" onclick="event.stopPropagation();app.openCalPicker('${task.id}')">📅</div>
      <div class="card-done-btn" onclick="event.stopagation();app.quickDone('${task.id}')">✓</div>
    </div>`;'''

# Let me check what the actual template literal looks like
import re
# Find renderCard
idx = src.find('renderCard(task,isDone=false){')
if idx >= 0:
    print(f"renderCard found at index {idx}")
    # Find the return statement in renderCard
    ret_idx = src.find("return`<div class=\"task-card\"", idx)
    if ret_idx >= 0:
        print(f"return found at index {ret_idx}")
        # Find the closing template literal
        end_ret = src.find("</div>`;", ret_idx)
        if end_ret >= 0:
            ret_content = src[ret_idx:end_ret+8]
            print(f"RenderCard return is {len(ret_content)} chars")

# Now let me rebuild the renderCard function body
# I need to:
# 1. Add countdown format computation BEFORE the return
# 2. Replace the return HTML

# Find the end of the card-meta line and card-cal-btn
# The section between renderCard opening and the return

# Insert countdown computation after 'let cc=...;'
old_cc_line = "let cc='ok-text';if(s.overdue)cc='overdue-text';else if(s.daysLeft!==null&&s.daysLeft<=3)cc='soon-text';"

new_cc_line = old_cc_line + """
    // 倒计时格式化:逾期-9/剩余+2/今天0
    let cdText='';
    if(s.daysLeft!==null&&s.daysLeft<0)cdText=String(s.daysLeft);
    else if(s.daysLeft!==null&&s.daysLeft===0)cdText='0';
    else if(s.daysLeft!==null&&s.daysLeft>0)cdText='+'+s.daysLeft;
    // 进度格子
    let dots='';
    const now=new Date();const yy=now.getFullYear(),mm=now.getMonth();
    function addDot(n,t){
      if(t==='旬'){dots='';for(let i=0;i<3;i++)dots+='<span class=\"prog-dot '+(i<n?'prog-on':'prog-off')+'\"></span>'}
      else if(t==='weekly'||(t==='monthly_multi'&&task.days&&task.days.length)){const mt=task.monthlyTarget||(task.days?task.days.length:4);dots='';for(let i=0;i<mt;i++)dots+='<span class=\"prog-dot '+(i<n?'prog-on':'prog-off')+'\"></span>'}
      else dots=''
    }
"""

# Replace the return HTML with new layout
old_ret = """    return`<div class="task-card ${sevClass} ${overdue?'overdue':''} ${doneClass}">
      <div class="card-body" onclick="app.openDetail('${task.id}')">
        <div class="card-top"><div class="card-name">${task.name}</div></div>
        <div class="card-meta"><div class="card-due">${s.dueDate?(task.type==='rolling'?'下次 '+fmtDateShort(s.dueDate):'截止 '+fmtDateShort(s.dueDate)):(s.label||'')}</div><div class="card-countdown ${cc}">${s.label}</div></div>
      </div>
      <div class="card-cal-btn" onclick="event.stopPropagation();app.openCalPicker('${task.id}')">📅</div>
      <div class="card-done-btn" onclick="event.stopPropagation();app.quickDone('${task.id}')">✓</div>
    </div>`;"""

# The actual string in the file might have different escaping
# Let me search for the EXACT pattern
ret_pattern = re.search(r"return`<div class=\"task-card", src)
if ret_pattern:
    print(f"Pattern found at {ret_pattern.start()}")
    # Print context around it
    context = src[ret_pattern.start():ret_pattern.start()+200]
    print(repr(context[:200]))
