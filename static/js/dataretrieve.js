console.log("retrieve records");
var records = window.localStorage.getItem("request_fullfillment");
var obj = JSON.parse(records);
console.log(obj);

if( obj ){
    document.getElementById("tno").value = obj.ticket_no;
    document.getElementById("ename").value = obj.emp_name;
    document.getElementById("eid").value = obj.emp_id;
    document.getElementById("tpriority").value = obj.priority;
    document.getElementById("tmodel").value = obj.asset_model;
    document.getElementById("tunits").value = obj.no_of_unit;
    document.getElementById("trequest_type").value = obj.service_type;
    document.getElementById("supportservice").value = obj.support_service;
    document.getElementById("tcomments").value = obj.additional_comment;
    document.getElementById("tstatus").value = obj.ticket_status;
    document.getElementById("tcreation").value = obj.creation_date;
}