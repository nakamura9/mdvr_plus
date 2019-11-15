function getCalendar(year, month){
    //2d array start from first day 
    var first = new Date(year, month, 1);
    console.log(first)
    var i;
    var dateArray = [];
    for(i=1;i < 32; i++){
        dateArray.push(new Date(year, month, i))
    }
    var filteredDateArray = dateArray.filter(function(date){
        return date.getMonth() == first.getMonth()
    })

    //add to array days before the first up to sunday
    var prefix = [];
    var suffix = [];
    var last = filteredDateArray[filteredDateArray.length -1];
    console.log(last)
    console.log(filteredDateArray)
    var firstWeekDay = first.getDay();
    var lastWeekDay = last.getDay();
    console.log(firstWeekDay)
    console.log(lastWeekDay)
    if( firstWeekDay > 0){
        for(i=1;i=firstWeekDay;i++){
            prefix.push(new Date(first - daysInMs(i)));
        }
    }
    
    if( lastWeekDay < 6){
        for(i=1;i< 7 - lastWeekDay;i++){
            console.log(last)
            suffix.push(new Date(last + daysInMs(i)));
        }
    }
    
    // add to array days after the last of the month, up to saturday
    console.log(prefix)
    console.log(suffix)

}

console.log(getCalendar(2019, 10));


function daysInMs(days){
    return days * 24 * 60 * 60 * 1000
}

