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
        check.style.backgroundColor = 'black';
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
        check.style.backgroundColor = 'black';
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

function inc(){
    let mins = parseInt(document.getElementById('pomoMin').innerText);
    //console.log(mins)
    document.getElementById('pomoMin').innerText = mins + 10;
}

function dec(){
    let mins = parseInt(document.getElementById('pomoMin').innerText);
    //console.log(mins)
    if(mins == 0){
        alert("Time cannot be negative!!")
    }else{
        document.getElementById('pomoMin').innerText = mins - 10;
    }
}

function pomo(){
    let mins = parseInt(document.getElementById('pomoMin').innerText);
    let secs = parseInt(document.getElementById('pomoSec').innerText);
    if(secs !== 0){
        console.log(secs)
        document.getElementById('pomoSec').innerText = secs - 1;
    }else{
        document.getElementById('pomoSec').innerText = 59;
        document.getElementById('pomoMin').innerText = mins-1;
    }
    if(mins == 0 && secs == 0){
        alert('pomo timer over')
        clearInterval(pomoInterval);
        document.getElementById('pomoSec').innerText = '00';
        document.getElementById('pomoMin').innerText = '00'
    }
}

function pomoStart(){
    pomoInterval = setInterval(pomo, 1000);
    pomoInterval;
}

function saveToDo(){
    localStorage.clear();
    for(let i = 0; i < localArr.length; i++){
        console.log(localArr[i])
        localStorage.setItem(i, localArr[i]);
    }
    scheduleSave();
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
    localStorage.setItem(weekDay.innerText, value);
}

function getSchedule(){
    let m = new DaySchedule(1, 2);
    m.create();
}
let addSchedule= document.getElementsByClassName('addSchedule');

function scheduleAdd(){
    let eventHolder = document.getElementById('eventConst');
    eventHolder.style.display = 'block';
    console.log('eventHolder');
}

let scheduleCounter = 0;

let eventHolder = document.getElementById('eventConst');
let schedule = document.getElementById('schedule');
let localEvt;
let eventName = document.getElementById('eventName');
let eventDate = document.getElementById('eventDate');
let eventDesc = document.getElementById('eventDesc');

function saveSchedule(){

    localEvt = [
        eventDate,
        eventDesc
    ]

    let a = scheduleCounter.toString()
    let sched = document.createElement('div');
    sched.classList.add('sched');
    let schedName = document.createElement('p');
    schedName.innerText = eventName.value;
    let schedTime = document.createElement('span');
    schedTime.innerText = eventDate.value;
    schedule.appendChild(sched);
    schedName.classList.add('schedName')
    schedName.id = 'schedName' + a;
    sched.appendChild(schedName);
    schedTime.classList.add('schedTime');
    schedTime.id = 'schedTime' + a;
    sched.appendChild(schedTime);
    eventHolder.style.display = 'none';
    scheduleCounter++;
}

function localSchedSave(n, d){
    let events = document.getElementsByClassName('sched'), i;
    //console.log(evtTime.innerText);
    for(i=0;i < events.length; i++){
        console.log(i)
        let k = 's'+ i;

    
        if(localStorage.getItem(k) == true){
            localStorage.removeItem(k);
        }
        
        a=i.toString()
        console.log(a)
        let evtTime = document.getElementById(d+ a);
        let evtName = document.getElementById(n+ a);
        console.log(evtTime, evtName)
        let v = evtName.innerText + '/' +evtTime.innerText;
        localStorage.setItem(k, v);
    }
    localStorage.setItem('schedCount', scheduleCounter);
}

function localSchedGet(){
    scheduleCounter = parseInt(localStorage.getItem('schedCount'));
    let i, sum = '',j, sum3;
    for(i=0;i<scheduleCounter; i++){
        let k = 's'+i;
        if(localStorage.getItem(k)[i] == '/'){
            sum+= localStorage.getItem(k)[i];
            sum2 = localStorage.getItem(k).replace(sum, '');
            for(j = 0; j < sum2.length; j++){
                sum3 += sum2[j];
            }
        }else{
            sum+= localStorage.getItem(k)[i];
        }
        localSchedSave(sum, sum3);
    }
}