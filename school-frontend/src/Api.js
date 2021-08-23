import { makePOST, makeGET } from "./helpers/RequestHelper"

const BASEURL = "https://school-pickup.herokuapp.com";

export const markAsDone = (phone, childFirst, childLast, cb) => {
    const route = (BASEURL ? BASEURL : "") + "/api/done";
    // console.log(`Marking phone number ${phone} as done...`)
    // console.log(JSON.stringify({ phone, childFirst, childLast }))
    makePOST(route, JSON.stringify({ phone, childFirst, childLast }), { 'Content-Type': 'application/json'}, (resp) => {
        console.log(resp);
        const { status } = resp;
        cb(status);
    });
}

export const fetchStudents = (cb) => {
    const route = (BASEURL ? BASEURL : "") + "/api/getlist";

    const reformat = (data) => {
        if(!data) return [];
        
        const processPoint = (point) => {
            return {
                time: point[0],
                phone: point[1],
                parentFirst: point[2],
                parentLast: point[3],
                childFirst: point[4],
                childLast: point[5],
                grade: point[6],
                message: point[7]
            }
        }

        var reformatted = {}

        const fetchKey = (grade) => {
            if(grade.startsWith("TOD")) {
                return "Toddler";
            } else if(grade.startsWith("INF")) {
                return "Infant";
            } else if(grade.startsWith("OLD INF") || grade.startsWith("OLDINF")) {
                return "Older Infant";
            } else if(grade.startsWith("PRE 3") || grade.startsWith("PRE3")) {
                return "Preschool 3";
            } else if(grade.startsWith("EPRE") || grade.startsWith("PRE 4") || grade.startsWith("PRE4") || grade.startsWith("EK")) {
                return "Preschool 4 / EK";
            }
            switch(grade) {
                case "K":
                case "01":
                case "02":
                case "03":
                case "04":
                case "05":
                case "06":
                case "07":
                case "08":
                    return "K-8";
                default:
                    return "Other";
            }
        }

        for(let i = 0; i < data.length; i++) {
            const point = processPoint(data[i]);
            const key = fetchKey(point.grade)
            if(Array.isArray(reformatted[key])) {
                reformatted[key].push(point);
            } else {
                reformatted[key] = [point]
            }
        }
        
        return reformatted;
    }

    makeGET(route, (resp) => {
        const students = reformat(resp);
        cb(students);
    });
}