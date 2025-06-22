let img = document.getElementById('img');
let hrs = document.getElementById('hrs');
let min = document.getElementById('min');
let time = document.getElementsByClassName('time')[0];
let inp = document.getElementById('inp');
let btn = document.getElementById('btn');
let save = document.getElementById('save');
let habitcont = document.getElementById('habitcontainer');


var todoCount = 0;
var store, localArr = [];

img.style.height = window.screen.height;
img.style.width = window.screen.width;

class ToDo{
    constructor(name, checked, num){
        this.name = name;
        this.checked = checked;
        this.num = num
    }
    create(){
        console.log('create started')

        let n = this.name;
        let c = this.checked;

        //todoCount++
        //console.log("works!!");
        addToDo(n, c);
}
}

class DaySchedule{
    constructor(n, string){
        this.n = n;
        this.string = string;
    }
    create(){
        console.log('create works!!')
        let weekDay = document.getElementById('WeekHead').innerText;
        let val = localStorage.getItem(weekDay);
        console.clear();
        console.log(val);
    }
}

function addToDo(n, c){
    let habitcont = document.getElementById('habitcontainer');
    let hab = document.createElement('div');
    hab.classList.add('hab');
    habitcont.appendChild(hab);
    todoCount++
    //console.log("works!!");
    let check = document.createElement('div');
    check.classList.add('check');
    if(c=='true'){
        check.style.backgroundColor = 'rgb(245, 237, 216)';
    }
    hab.appendChild(check);
    check.addEventListener( 'click', changeCol);
    hab.addEventListener('dblclick', remove)
    
    function remove(){
        habitcont.removeChild(hab);
        console.log(localArr)
        for(let i=0;i<localArr.length;i++){
            console.log(cont)
            if(localArr[i][0]==cont.innerText){
                //console.log('value of i'+ document.getElementsByClassName('cont')[i].innerText;
                localArr.splice(i,1);
                console.log(localArr);
            }
        }
    }

    function changeCol(){
        check.style.backgroundColor = 'rgb(245, 237, 216)';
        for(let i = 0; i < localArr.length; i++){
            console.log(localArr[i], cont)
            if(localArr[i][0] == cont.innerText){
                localArr.splice(i, 1)
                console.log(localArr)
            }
        }
        localArr.push([cont.innerText, true])
    }

    let cont = document.createElement('p');
    cont.classList.add('cont');
    cont.innerText = n;
    hab.appendChild(cont)
    store = [
        n,
        c
    ]
    localArr.push(store);
    console.log(store);
    //localStorage.setItem(inp.value, store);
    //console.log(localStorage.getItem(store[0]));
}
function start(){
    let motiv = document.getElementById('motiv');
    let n = Math.random() * 8;
    if(n<1){
        motiv.innerText = "Every step forward counts, no matter how small--keep moving toward your dreams."
    }else if(n<2){
        motiv.innerText = "Challenges are just opportunities in disguise; embrace them and grow."
    }else if(n<3){
        motiv.innerText = "Your potential is limitless when you believe in yourself and take action."
    }else if(n<4){
        motiv.innerText = "Success is not the absence of obstacles, but the courage to push through them."
    }else if(n<5){
        motiv.innerText = "Your future is built by the choices you make today--choose boldly."
    }else if(n<6){
        motiv.innerText = "You do not need to be perfect to start, but you need to start to become great."
    }else if(n<7){
        motiv.innerText = "The only limits are the ones you set for yourself--break free and soar."
    }else if(n<8){
        motiv.innerText = "Turn your setbacks into comebacks with determination and grit."
    }
    for (let i=0; i<i+1; i++){
        let k;
        if(localStorage.getItem(i)==undefined){
            break;
        }
        let string = '';
        let n, c;
        for(let j=0;localStorage[i][j] !== ','; j++){
            string += localStorage[i][j];
            k=j
        }
        n=string;
        string=''
        for(k; localStorage[i][k+2] !== undefined; k++){
            string += localStorage[i][k+2];
        }
        c=string;
        console.log(n, c)
        let m = new ToDo(n, c, i);
        m.create()
    }  
    setInterval(draw, 1000);
    localSchedGet()
}

function draw(){
    const d = new Date();
    hrs.innerHTML = d.getHours();
    min.innerHTML = d.getMinutes();

    let hours = parseInt(hrs.innerHTML);
    let mins = parseInt(min.innerHTML);
    if(hours < 10){
        hrs.innerHTML = '0'+d.getHours();
    }
    if(mins < 10){
        min.innerHTML = '0'+d.getHours();
    }
}

function loadToDos(){
    for (let i=0; i<i+1; i++){
        let k;
        if(localStorage.getItem(i)==undefined){
            break;
        }
        let string = '';
        let n, c;
        for(let j=0;localStorage[i][j] !== ','; j++){
            string += localStorage[i][j];
            k=j
        }
        n=string;
        string=''
        for(k; localStorage[i][k+2] !== undefined; k++){
            string += localStorage[i][k+2];
        }
        c=string;
        console.log(n, c)
        let m = new ToDo(n, c, i);
        m.create()
    }  
}
let pomoCounter = 0;
function inc(){
    let mins = parseInt(document.getElementById('pomoMin').innerText);
    //console.log(mins)
    document.getElementById('pomoMin').innerText = mins + 10;
}

function dec(){
    let t = 0
    let mins = parseInt(document.getElementById('pomoMin').innerText);
    //console.log(mins)
    if(mins == 10){
        console.log(mins)
        document.getElementById('pomoMin').innerText = '00'
        t = 1
    }
    if(mins == 0){
        alert("Time cannot be negative!!")
    }else{
        if(t == 0){
            document.getElementById('pomoMin').innerText = mins - 10;
        }
    }
}

function pomo(){
    let mins = parseInt(document.getElementById('pomoMin').innerText);
    let secs = parseInt(document.getElementById('pomoSec').innerText);
    let nextMins = mins - 1;
    console.log('0'+mins)
    console.log(nextMins);
    if(nextMins == 9){document.getElementById('pomoMin').innerText = '0'+mins}
    if(nextMins < 10){
        document.getElementById('pomoMin').innerText = '0'+(mins);
    }
    if(secs !== 0){
        if(secs < 10 || secs == 10){
            document.getElementById('pomoSec').innerText = '0'+(secs - 1);
        }else{
            document.getElementById('pomoSec').innerText = secs - 1;
        }
    }else{
        document.getElementById('pomoSec').innerText = 59;
        document.getElementById('pomoMin').innerText = mins-1;
    }
    if(mins == 0 && secs == 0){
        alert('pomo timer over')
        clearInterval(pomoInterval);
        document.getElementById('pomoSec').innerText = '00';
        document.getElementById('pomoMin').innerText = '00'
        pomoCounter = 0;
    }
}

function pomoStart(){
    if(pomoCounter == 0){
        console.log('start!!')
        pomoInterval = setInterval(pomo, 1000);
        pomoCounter = 1
    }else{
        console.log('stop!!')
    }
    //pomoCounter;
}

function saveToDo(){
    localStorage.clear();
    for(let i = 0; i < localArr.length; i++){
        console.log(localArr[i])
        localStorage.setItem(i, localArr[i]);
    }
    localSchedSave();
}

function openDay(evt, day) {
  let weekHead = document.getElementById('WeekHead');
  if(day=='Sun'){
    weekHead.innerText = "Sunday"
  }else if(day == 'Mon'){
    weekHead.innerText = "Monday"
  }else if(day=='Tue'){
    weekHead.innerText = "Tuesday"
  }else if(day=='Wed'){
    weekHead.innerText = "Wednesday"
  }else if(day=='Thur'){
    weekHead.innerText = "Thursday"
  }else if(day=='Fri'){
    weekHead.innerText = "Friday"
  }else if(day=='Sat'){
    weekHead.innerText = "Saturday"
  }
  console.log(weekHead.innerText)
  getSchedule();
}

function scheduleEntry(){
    let sinp = document.getElementById('scheduleInp');
    let sp = document.getElementById('schedulePara');
    let WeekHead = document.getElementById('WeekHead')

    if(sp.innerText == 'click on a weekday to see schedule.'){
        sp.innerText=''
    }
    let li = document.createElement('li');
    li.classList.add('scheduleLists');
    li.innerText = sinp.value;
    sp.appendChild(li);
}

function scheduleSave(){
    let li = document.getElementsByClassName('scheduleLists');
    console.log(li)
    let weekDay = document.getElementById('WeekHead');
    let value, save;
    console.log('li length:'+li.length)
    for(let i = 0; i < li.length; i++){
        value += ' '+ li[i].innerText;
    }
    //localStorage.setItem(weekDay.innerText, value);
}

function getSchedule(){
    let m = new DaySchedule(1, 2);
    m.create();
}
let addSchedule= document.getElementsByClassName('addSchedule');

function scheduleAdd(){
    eventHolder.style.display = 'block';
    eventDecor.style.display = 'block';
    console.log('eventHolder');
    let frameHolder = document.getElementById('frameHolder');
    frameHolder.style.bottom = '1010px'
    let tablinks = document.getElementsByClassName('tablinks');
    tablinks[0].style.bottom = '1010px'
    tablinks[1].style.bottom = '1010px'
    tablinks[2].style.bottom = '1010px'
    tablinks[3].style.bottom = '1010px'
}

let scheduleCounter = 0;

let eventHolder = document.getElementById('eventConst');
let eventDecor = document.getElementById('schedEvtDec');
//let schedule = document.getElementById('schedule');
let localEvt = [];
let eventName = document.getElementById('eventName');
let eventDate = document.getElementById('eventDate');
let eventDesc = document.getElementById('eventDesc');

function saveSchedule(nv, dv, de){
    let schedulePara = document.getElementById('schedulePara');
    schedulePara.innerText = '';

    let a = scheduleCounter.toString()
    let sched = document.createElement('div');
    sched.classList.add('sched');
    let schedName = document.createElement('p');
    let schedTime = document.createElement('span');
    let schedDesc = document.createElement('p');
    if(nv && dv && de){
        schedName.innerText = nv//eventName.value;
        schedTime.innerText = dv //eventDate.value;
        schedDesc.innerText = de
        console.log('de'+de)
    }else{
        schedName.innerText = eventName.value;
        schedTime.innerText = eventDate.value;
        schedDesc.innerText = eventDesc.value;
    }
    
    schedDesc.classList.add('schedDesc');
    sched.appendChild(schedDesc);
    sched.classList.add('sched')
    console.log(schedDesc)
    sched.addEventListener('click', openDesc)
    sched.addEventListener('dblclick', delSched);

    function delSched(){
        let schedNames = document.getElementById('schedName')
        for(let i = 0; i < localEvt.length; i++){
            if(localEvt[i][0] === schedName.innerText){
                console.log('seen')
                localEvt.splice(i,1);
            }
        }
        //console.log(localEvt[0][0]);
        //console.log('schedName: '+schedName.innerText);
        //console.log('delSched')
        listCont.removeChild(sched);
    }

    function openDesc(){
        let evtInfo = document.getElementById('evtInfo');
        evtInfo.style.display = 'block';
        let btn = document.createElement('button');
        btn.innerText = 'x';
        btn.classList.add('closeInfo')
        btn.addEventListener('click', closeInfo);
        evtInfo.innerText = 'description: '+schedDesc.innerText;
        evtInfo.appendChild(btn);
    }
    let c = 0;
    let listCont = document.getElementById('listCont');
    listCont.appendChild(sched);
    if(schedTime.innerText[2] !== '/' && schedTime.innerText[5] !== '/'){
        alert('incorrect format!!'+schedTime.innerText[2])
        listCont.removeChild(sched)
        c=1
    }
    schedName.classList.add('schedName');
    //schedName.id = 'schedName' + a;
    sched.appendChild(schedName);
    schedTime.classList.add('schedTime');
    //schedTime.id = 'schedTime' + a;
    sched.appendChild(schedTime);
    let activity = document.createElement('div')
activity.classList.add('activity')
    let sum
    for(let j = 0; j < schedTime.innerText.length; j++){
        if(j==2){continue}
        if(j==5){continue}
        sum+=schedTime.innerText[j];
        sum.replace('undefined','')
        let sum1, sum2, sum3;
        sum1 = sum[0] +sum[1]
        sum2 = sum[2] + sum[3]
        sum3 = sum[4] + sum[5]
        let b = new Date()
        if(parseInt(sum1) == b.getDate() && parseInt(sum2) == b.getMonth()){
            activity.style.backgroundColor = 'green'
        }
        console.log(sum1)
        console.log(sum2)
    }
    console.log(schedTime)
    console.log(sum)
    //sched.appendChild(activity)
    eventHolder.style.display = 'none';
    eventDecor.style.display = 'none';
    scheduleCounter++;
    //let saveBtn = document.getElementById('saveBtn');
    //saveBtn.addEventListener('click', localSchedSave);


    let evtArr = [
        schedName.innerText,
        schedTime.innerText,
        schedDesc.innerText
    ]
    if(c == 0){
        localEvt.push(evtArr);
    }
    //console.log(localEvt)
    
    let frameHolder = document.getElementById('frameHolder');
    frameHolder.style.bottom = '610px'
    let tablinks = document.getElementsByClassName('tablinks');
    tablinks[0].style.bottom = '610px'
    tablinks[1].style.bottom = '610px'
    tablinks[2].style.bottom = '610px' 
    tablinks[3].style.bottom = '610px'
}

function localSchedSave(){
    console.log('localSchedSave')
    let i;
    for(i = 0; i < i+1; i++){
        let k = 's'+i;
        //console.log(k)
        if(localStorage.getItem(k)){
            //console.log('sched Save: '+localStorage.getItem(k))
            localStorage.removeItem(k);
        }else{
            localSchedSave2()
            break;
        }
    }
}

function localSchedSave2(){
    console.log(localEvt)
    let i;
    for(i=0;i<localEvt.length;i++){
        let k = 's'+i;
        let v = localEvt[i];
        console.log(k, v);
        localStorage.setItem(k, v);
    }
}

function localSchedGet(){
    for(let i = 0; i < localStorage.length; i++){
        let k = 's'+i, sum = '',sum2 = '', sum3 = '';
        if(localStorage.getItem(k) == undefined){
            break;
        }
        let localItm = localStorage.getItem(k)
        console.log(localItm);
        for(let j = 0; j < localItm.length; j++){
            if(localItm[j] == ','){
                //console.log(sum)
                for(j++; j<localItm.length; j++){
                    if(localItm[j] == ','){
                        //console.log(sum2)
                        for(j++; j<localItm.length; j++){
                            
                            sum3 += localItm[j];
                        }
                    }
                    if(localItm[j] == undefined){continue}
                    sum2 += localItm[j];
                }
                saveSchedule(sum, sum2, sum3);
                console.log('sum2'+sum2)
                break;
            }else{
                sum+= localItm[j];
            }
        }
    }
}

function closeInfo(){
    let evtInfo = document.getElementById('evtInfo');
    evtInfo.style.display = 'none'
}

function frame(evt, link) {
let iframe = document.getElementsByClassName('yes');
for(let i = 0; i < iframe.length; i++){
    iframe[i].style.display = 'none'
}
iframe[link].style.display = 'block'
//console.log(iframe[link])
}