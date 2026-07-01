import re

with open('/home/oiio/橙子的工作台/运营RUSH/index.html', 'r', encoding='utf-8') as f:
    src = f.read()

changes = []

# 1. resolveDay: support day=-2 (last day of month)
old = "function resolveDay(taskDay,year,month){if(taskDay===-1)return new Date(year,month+1,0).getDate()-1;return taskDay}"
new = "function resolveDay(taskDay,year,month){if(taskDay===-2)return new Date(year,month+1,0).getDate();if(taskDay===-1)return new Date(year,month+1,0).getDate()-1;return taskDay}"
assert old in src, "resolveDay not found"
src = src.replace(old, new)
changes.append("resolveDay: added day=-2 support")

# 2. call_9999 task definition
old = "{id:'call_9999',name:'打9999',type:'monthly_multi',severity:'red',days:[25,26,27,1],reviews:[],note:'',completions:{},typeLabel:'月度 · 4次/月',desc:'每月25、26、27号及次月1号各打一次，共4次。每次独立标记。25/26/27号遇周六提前至周五，次月1号遇周六推迟至周日。'}"
new = "{id:'call_9999',name:'打9999',type:'monthly_multi',severity:'red',days:[],lastNDays:4,reviews:[],note:'',completions:{},typeLabel:'月度 · 最后4天',desc:'每月最后4天各完成一次（交易代码9999），共4次。每次独立标记。倒数第4天起进入待处理。'}"
assert old in src, "call_9999 not found"
src = src.replace(old, new)
changes.append("call_9999: lastNDays=4, updated label/desc")

# 3. personal_security task definition
old = "{id:'personal_security',name:'个人安保学习本',type:'monthly_fixed',severity:'yellow',day:-1,postponeSat:true,reviews:[],note:'',lastCompleted:null,typeLabel:'月度 · 每月倒数第2天',desc:'每月倒数第2天完成。遇周六推迟至周日。'}"
new = "{id:'personal_security',name:'个人安保学习本',type:'monthly_fixed',severity:'yellow',day:-2,postponeSat:true,reviews:[],note:'',lastCompleted:null,typeLabel:'月度 · 每月最后1天',desc:'每月最后1天完成。遇周六推迟至周日。'}"
assert old in src, "personal_security not found"
src = src.replace(old, new)
changes.append("personal_security: day=-2, updated label/desc")

# 4. Migration: sync call_9999 lastNDays
old = "if(t.id==='safety_check'){if(!t.multiCompletion)t.multiCompletion=true;if(!t.monthlyTarget)t.monthlyTarget=4;if(!t.completionHistory)t.completionHistory=[];t.weekStart=1}"
new = "if(t.id==='safety_check'){if(!t.multiCompletion)t.multiCompletion=true;if(!t.monthlyTarget)t.monthlyTarget=4;if(!t.completionHistory)t.completionHistory=[];t.weekStart=1}if(t.id==='call_9999'){t.lastNDays=4;if(!t.completions)t.completions={}}"
assert old in src, "safety_check migration not found"
src = src.replace(old, new)
changes.append("Migration: call_9999 gets lastNDays=4")

# 5. Remove severity labels
old = "sevLabel(s){return{red:'🔴 必须',yellow:'🟡 重要',green:'🟢 建议'}[s]||s}"
new = "sevLabel(s){return''}"
assert old in src, "sevLabel not found"
src = src.replace(old, new)
changes.append("sevLabel: returns empty string")

# Remove card-tag span
old = "<span class=\"card-tag\">${this.sevLabel(task.severity)}</span>"
new = ""
assert old in src, "card-tag not found"
src = src.replace(old, new)
changes.append("renderCard: removed severity tag span")

# 6. getMultiStatus: add lastNDays
old = """  getMultiStatus(task,today){
    const m=today.getMonth(),y=today.getFullYear();
    // Determine active cycle: find most recent 25th
    let cycleMonth,cycleYear;
    if(today.getDate()>=25){cycleMonth=m;cycleYear=y}
    else{cycleMonth=m===0?11:m-1;cycleYear=m===0?y-1:y}
    // Build 4 targets: cycleMonth 25/26/27 + cycleMonth+1 1st
    const targets=[];
    for(const day of task.days){
      let target;
      if(day===1)target=new Date(cycleYear,cycleMonth+1,1);
      else target=new Date(cycleYear,cycleMonth,day);
      if(day===1){if(isSaturday(target))target=postponeIfSaturday(target)}
      else{if(isSaturday(target))target=postponeToFriday(target)}
      const key=`${target.getFullYear()}-${target.getMonth()}-${target.getDate()}`;
      const done=task.completions&&task.completions[key];
      targets.push({target,key,done});
    }
    const pending=targets.filter(t=>!t.done);
    if(!pending.length){
      // Current cycle done, show next cycle
      const nextTargets=[];
      for(const day of task.days){
        let target;
        if(day===1)target=new Date(cycleYear,cycleMonth+2,1);
        else target=new Date(cycleYear,cycleMonth+1,day);
        if(day===1){if(isSaturday(target))target=postponeIfSaturday(target)}
        else{if(isSaturday(target))target=postponeToFriday(target)}
        const key=`${target.getFullYear()}-${target.getMonth()}-${target.getDate()}`;
        nextTargets.push({target,key,done:task.completions&&task.completions[key]});
      }
      const nextPending=nextTargets.filter(t=>!t.done);
      if(!nextPending.length)return{status:'done',label:'本月全部完成',dueDate:null,daysLeft:null,overdue:false};
      const u=nextPending[0];
      const dl=daysBetween(today,u.target);
      if(dl===0)return{status:'today',label:`今天到期 · 还剩${nextPending.length}次`,dueDate:u.target,daysLeft:0,overdue:false};
      return{status:'ok',label:`还有${dl}天 · 还剩${nextPending.length}次`,dueDate:u.target,daysLeft:dl,overdue:false};
    }
    const u=pending[0];
    const dl=daysBetween(today,u.target);
    if(dl<0)return{status:'overdue',label:`逾期${-dl}天 · 还剩${pending.length}次`,dueDate:u.target,daysLeft:dl,overdue:true};
    if(dl===0)return{status:'today',label:`今天到期 · 还剩${pending.length}次`,dueDate:u.target,daysLeft:0,overdue:false};
    return{status:'ok',label:`还有${dl}天 · 还剩${pending.length}次`,dueDate:u.target,daysLeft:dl,overdue:false};
  }"""

new = """  getMultiStatus(task,today){
    const m=today.getMonth(),y=today.getFullYear();
    // lastNDays mode: dynamic last N days of current month
    if(task.lastNDays){
      if(!task.completions)task.completions={};
      const monthEnd=new Date(y,m+1,0);
      const lastDay=monthEnd.getDate();
      const startDay=lastDay-task.lastNDays+1;
      const targets=[];
      for(let d=startDay;d<=lastDay;d++){
        const target=new Date(y,m,d);
        const key=`${target.getFullYear()}-${target.getMonth()}-${target.getDate()}`;
        const done=task.completions&&task.completions[key];
        targets.push({target,key,done});
      }
      const pending=targets.filter(t=>!t.done);
      if(!pending.length)return{status:'done',label:'本月全部完成',dueDate:null,daysLeft:null,overdue:false};
      const firstPending=pending[0];
      const dl=daysBetween(today,firstPending.target);
      const fourthToLast=new Date(y,m,startDay);
      if(today<fourthToLast)return{status:'ok',label:`还有${daysBetween(today,fourthToLast)}天开始 · 共${task.lastNDays}次`,dueDate:fourthToLast,daysLeft:daysBetween(today,fourthToLast),overdue:false};
      if(dl<0)return{status:'overdue',label:`逾期${-dl}天 · 还剩${pending.length}次`,dueDate:firstPending.target,daysLeft:dl,overdue:true};
      if(dl===0)return{status:'today',label:`今天到期 · 还剩${pending.length}次`,dueDate:firstPending.target,daysLeft:0,overdue:false};
      return{status:'pending',label:`还剩${pending.length}次 · 截止${fmtDateShort(targets[targets.length-1].target)}`,dueDate:firstPending.target,daysLeft:dl,overdue:false};
    }
    // Original cycle mode
    let cycleMonth,cycleYear;
    if(today.getDate()>=25){cycleMonth=m;cycleYear=y}
    else{cycleMonth=m===0?11:m-1;cycleYear=m===0?y-1:y}
    const targets=[];
    for(const day of task.days){
      let target;
      if(day===1)target=new Date(cycleYear,cycleMonth+1,1);
      else target=new Date(cycleYear,cycleMonth,day);
      if(day===1){if(isSaturday(target))target=postponeIfSaturday(target)}
      else{if(isSaturday(target))target=postponeToFriday(target)}
      const key=`${target.getFullYear()}-${target.getMonth()}-${target.getDate()}`;
      const done=task.completions&&task.completions[key];
      targets.push({target,key,done});
    }
    const pending=targets.filter(t=>!t.done);
    if(!pending.length){
      const nextTargets=[];
      for(const day of task.days){
        let target;
        if(day===1)target=new Date(cycleYear,cycleMonth+2,1);
        else target=new Date(cycleYear,cycleMonth+1,day);
        if(day===1){if(isSaturday(target))target=postponeIfSaturday(target)}
        else{if(isSaturday(target))target=postponeToFriday(target)}
        const key=`${target.getFullYear()}-${target.getMonth()}-${target.getDate()}`;
        nextTargets.push({target,key,done:task.completions&&task.completions[key]});
      }
      const nextPending=nextTargets.filter(t=>!t.done);
      if(!nextPending.length)return{status:'done',label:'本月全部完成',dueDate:null,daysLeft:null,overdue:false};
      const u=nextPending[0];
      const dl=daysBetween(today,u.target);
      if(dl===0)return{status:'today',label:`今天到期 · 还剩${nextPending.length}次`,dueDate:u.target,daysLeft:0,overdue:false};
      return{status:'ok',label:`还有${dl}天 · 还剩${nextPending.length}次`,dueDate:u.target,daysLeft:dl,overdue:false};
    }
    const u=pending[0];
    const dl=daysBetween(today,u.target);
    if(dl<0)return{status:'overdue',label:`逾期${-dl}天 · 还剩${pending.length}次`,dueDate:u.target,daysLeft:dl,overdue:true};
    if(dl===0)return{status:'today',label:`今天到期 · 还剩${pending.length}次`,dueDate:u.target,daysLeft:0,overdue:false};
    return{status:'ok',label:`还有${dl}天 · 还剩${pending.length}次`,dueDate:u.target,daysLeft:dl,overdue:false};
  }"""

assert old in src, "getMultiStatus not found"
src = src.replace(old, new)
changes.append("getMultiStatus: added lastNDays branch")

# 7. completeTask: add lastNDays
old = """    if(task.type==='monthly_multi'){
      if(!task.completions)task.completions={};
      // 与getMultiStatus使用相同的周期计算
      const m=targetDate.getMonth(),y=targetDate.getFullYear();
      let cycleMonth,cycleYear;
      if(targetDate.getDate()>=25){cycleMonth=m;cycleYear=y}
      else{cycleMonth=m===0?11:m-1;cycleYear=m===0?y-1:y}
      // 构建当前周期的targets
      const cycleTargets=[];
      for(const day of task.days){
        let d;if(day===1)d=new Date(cycleYear,cycleMonth+1,1);else d=new Date(cycleYear,cycleMonth,day);
        cycleTargets.push({d,key:`${d.getFullYear()}-${d.getMonth()}-${d.getDate()}`});
      }
      // 优先标记targetDate当天，否则标记第一个未完成的
      let matched=false;
      const tdKey=`${targetDate.getFullYear()}-${targetDate.getMonth()}-${targetDate.getDate()}`;
      for(const t of cycleTargets){
        if(t.key===tdKey&&!task.completions[t.key]){task.completions[t.key]=now;matched=true;break}
      }
      if(!matched){
        for(const t of cycleTargets){
          if(!task.completions[t.key]){task.completions[t.key]=now;break}
        }
      }
    }"""

new = """    if(task.type==='monthly_multi'){
      if(!task.completions)task.completions={};
      if(task.lastNDays){
        const m=targetDate.getMonth(),y=targetDate.getFullYear();
        const monthEnd=new Date(y,m+1,0);
        const lastDay=monthEnd.getDate();
        const startDay=lastDay-task.lastNDays+1;
        const targets=[];
        for(let d=startDay;d<=lastDay;d++){
          const dt=new Date(y,m,d);
          targets.push({d:dt,key:`${dt.getFullYear()}-${dt.getMonth()}-${dt.getDate()}`});
        }
        let matched=false;
        const tdKey=`${targetDate.getFullYear()}-${targetDate.getMonth()}-${targetDate.getDate()}`;
        for(const t of targets){
          if(t.key===tdKey&&!task.completions[t.key]){task.completions[t.key]=now;matched=true;break}
        }
        if(!matched){
          for(const t of targets){
            if(!task.completions[t.key]){task.completions[t.key]=now;break}
          }
        }
      }else{
        const m=targetDate.getMonth(),y=targetDate.getFullYear();
        let cycleMonth,cycleYear;
        if(targetDate.getDate()>=25){cycleMonth=m;cycleYear=y}
        else{cycleMonth=m===0?11:m-1;cycleYear=m===0?y-1:y}
        const cycleTargets=[];
        for(const day of task.days){
          let d;if(day===1)d=new Date(cycleYear,cycleMonth+1,1);else d=new Date(cycleYear,cycleMonth,day);
          cycleTargets.push({d,key:`${d.getFullYear()}-${d.getMonth()}-${d.getDate()}`});
        }
        let matched=false;
        const tdKey=`${targetDate.getFullYear()}-${targetDate.getMonth()}-${targetDate.getDate()}`;
        for(const t of cycleTargets){
          if(t.key===tdKey&&!task.completions[t.key]){task.completions[t.key]=now;matched=true;break}
        }
        if(!matched){
          for(const t of cycleTargets){
            if(!task.completions[t.key]){task.completions[t.key]=now;break}
          }
        }
      }
    }"""

assert old in src, "completeTask monthly_multi not found"
src = src.replace(old, new)
changes.append("completeTask: added lastNDays branch")

# 8. isMonthFullyComplete: add lastNDays
old = """    if(task.type==='monthly_multi'){
      if(!task.completions||!task.days)return false;
      return task.days.every(day=>{let d;if(day===1)d=new Date(y,m+1,1);else d=new Date(y,m,day);const key=`${d.getFullYear()}-${d.getMonth()}-${d.getDate()}`;return!!task.completions[key]});
    }"""

new = """    if(task.type==='monthly_multi'){
      if(!task.completions)return false;
      if(task.lastNDays){
        const monthEnd=new Date(y,m+1,0);
        const lastDay=monthEnd.getDate();
        const startDay=lastDay-task.lastNDays+1;
        for(let d=startDay;d<=lastDay;d++){
          const dt=new Date(y,m,d);
          const key=`${dt.getFullYear()}-${dt.getMonth()}-${dt.getDate()}`;
          if(!task.completions[key])return false;
        }
        return true;
      }
      if(!task.days)return false;
      return task.days.every(day=>{let d;if(day===1)d=new Date(y,m+1,1);else d=new Date(y,m,day);const key=`${d.getFullYear()}-${d.getMonth()}-${d.getDate()}`;return!!task.completions[key]});
    }"""

assert old in src, "isMonthFullyComplete monthly_multi not found"
src = src.replace(old, new)
changes.append("isMonthFullyComplete: added lastNDays branch")

# 9. Detail modal monthly_multi display
old = """    if(task.type==='monthly_multi'){const today=new Date(),m=today.getMonth(),y=today.getFullYear();let cycleMonth,cycleYear;if(today.getDate()>=25){cycleMonth=m;cycleYear=y}else{cycleMonth=m===0?11:m-1;cycleYear=m===0?y-1:y}html+=`<div class=\"modal-section\"><div class=\"modal-section-title\">各节点状态</div>`;task.days.forEach(day=>{let target;if(day===1)target=new Date(cycleYear,cycleMonth+1,1);else target=new Date(cycleYear,cycleMonth,day);const key=`${target.getFullYear()}-${target.getMonth()}-${target.getDate()}`;const done=task.completions&&task.completions[key];html+=`<div class=\"modal-info-row\"><span class=\"label\">${fmtDate(target)}</span><span class=\"value\" style=\"color:${done?'var(--green)':'var(--red)'}\">${done?'✅ 已完成':'🔴 待完成'}</span></div>`});html+=`</div>`}"""

new = """    if(task.type==='monthly_multi'){const today=new Date(),m=today.getMonth(),y=today.getFullYear();if(task.lastNDays){const monthEnd=new Date(y,m+1,0);const lastDay=monthEnd.getDate();const startDay=lastDay-task.lastNDays+1;html+=`<div class=\"modal-section\"><div class=\"modal-section-title\">各节点状态（倒数${task.lastNDays}天）</div>`;for(let d=startDay;d<=lastDay;d++){const dt=new Date(y,m,d);const key=`${dt.getFullYear()}-${dt.getMonth()}-${dt.getDate()}`;const done=task.completions&&task.completions[key];html+=`<div class=\"modal-info-row\"><span class=\"label\">${fmtDate(dt)}</span><span class=\"value\" style=\"color:${done?'var(--green)':'var(--red)'}\">${done?'✅ 已完成':'🔴 待完成'}</span></div>`}html+=`</div>`}else{let cycleMonth,cycleYear;if(today.getDate()>=25){cycleMonth=m;cycleYear=y}else{cycleMonth=m===0?11:m-1;cycleYear=m===0?y-1:y}html+=`<div class=\"modal-section\"><div class=\"modal-section-title\">各节点状态</div>`;task.days.forEach(day=>{let target;if(day===1)target=new Date(cycleYear,cycleMonth+1,1);else target=new Date(cycleYear,cycleMonth,day);const key=`${target.getFullYear()}-${target.getMonth()}-${target.getDate()}`;const done=task.completions&&task.completions[key];html+=`<div class=\"modal-info-row\"><span class=\"label\">${fmtDate(target)}</span><span class=\"value\" style=\"color:${done?'var(--green)':'var(--red)'}\">${done?'✅ 已完成':'🔴 待完成'}</span></div>`});html+=`</div>`}}"""

assert old in src, "detail modal monthly_multi not found"
src = src.replace(old, new)
changes.append("detail modal monthly_multi: added lastNDays branch")

# Write
with open('/home/oiio/橙子的工作台/运营RUSH/index.html', 'w', encoding='utf-8') as f:
    f.write(src)

print("=== All changes applied ===")
for c in changes:
    print(f"  OK {c}")

open_b = src.count('{')
close_b = src.count('}')
print(f"\nBraces: {{ = {open_b} }} = {close_b} {'BALANCED' if open_b == close_b else 'IMBALANCE'}")

checks = [
    ("resolveDay day=-2", "if(taskDay===-2)return new Date(year,month+1,0).getDate()"),
    ("call_9999 lastNDays=4", "lastNDays:4"),
    ("personal_security day=-2", "day:-2"),
    ("call_9999 migration", "if(t.id==='call_9999'){t.lastNDays=4"),
    ("sevLabel empty", "sevLabel(s){return''}"),
    ("no card-tag", "<span class=\"card-tag\">${this.sevLabel("),
    ("getMultiStatus lastNDays", "if(task.lastNDays){"),
    ("completeTask lastNDays", "if(task.lastNDays){"),
    ("isMonthFullyComplete lastNDays", "if(task.lastNDays){"),
    ("detail modal lastNDays", "倒数"),
]
for name, pattern in checks:
    found = pattern in src
    print(f"  {'OK' if found else 'MISS'} {name}")

print(f"\nFile size: {len(src)} chars")
