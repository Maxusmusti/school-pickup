import React, {useState, useEffect} from 'react';
import './App.css';

import { markAsDone, fetchStudents } from "./Api";

const TodoList = (props) => {
  var items = props.items.map((item, index) => {
    return (
      <>
        <TodoListItem key={index} item={item} index={index} parent={props.parent} removeItem={props.removeItem} markTodoDone={props.markTodoDone} />
        <hr />
      </>
    );
  })
  return (
  <ul className="list-group"> {items} </ul>
  );
}

const TodoListItem = (props) => {

  const onClickDone = () => {
    props.markTodoDone(props.item.phone, props.item.childFirst, props.item.childLast, props.index, props.parent);
  }

  const formatTime = (time) => new Date(Date.parse(time)).toLocaleString('en-US', { hour: 'numeric', minute: 'numeric', hour12: true })
  
  var todoClass = props.item.done ? "done" : "undone";
    return(
      <li className="list-group-item ">
        <div className={todoClass} onClick={onClickDone}>
          <p>{`${props.item.parentFirst} ${props.item.parentLast} picking up` } <b style={{color: "#FFFFFF"}}>{`${props.item.childFirst} ${props.item.childLast}`}</b>{` in grade ${props.item.grade}`}</p>
          <p>{`${props.item.message}`}</p>
          <p>{`${props.item.phone} || ${formatTime(props.item.time)}`}</p>
        </div>
      </li>     
    );
}

const TodoHeader = (props) => {
  const fetchDate = () => {
    var today = new Date();
    var dd = String(today.getDate()).padStart(2, '0');
    var mm = String(today.getMonth() + 1).padStart(2, '0'); //January is 0!
    var yyyy = today.getFullYear();

    today = mm + '/' + dd + '/' + yyyy;
    return today;
  }
  
  return (
    <h1 style={{marginBottom: '8vh', textAlign: 'center'}}>School Pick Up: {fetchDate()}</h1>
  );
}

const App = () => {

  const [todos, setTodos] = useState({});
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const getStudents = () => {
      fetchStudents((result) => {
        setIsLoading(false);
        setTodos(result)
      })
    }
    getStudents();
    const interval = setInterval(() => getStudents(), 10000);
    return () => {
      clearInterval(interval);
    }
  }, [])

  const markTodoDone = (phoneNumber, childFirst, childLast, itemIndex, key) => {
    if(window.confirm("Are you sure that you want to mark this entry as completed?")) {
      setIsLoading(true);
      var todoItems = todos;
      markAsDone(phoneNumber, childFirst, childLast, (status) => {
        if(status === false) {
          setIsLoading(false)
          alert("Failed to mark this student as picked up! Please try again later")
        } else {
          var todo = todoItems[key][itemIndex];
          todoItems[key].splice(itemIndex, 1);
          todo.done = !todo.done;
          todo.done ? todoItems[key].push(todo) : todoItems[key].unshift(todo);
          setIsLoading(false)
          setTodos(todoItems)
        }
      })
    }
  }

  if(isLoading) return <span>Loading...</span>;

  const sortingMap = {
    "Infant": 0,
    "Older Infant": 1,
    "Toddler": 2,
    "Preschool 3": 3,
    "Preschool 4 / EK": 4,
    "K-8": 5,
    "Other": 6
}

  return (
    <div id="main">
        <TodoHeader />
        <div style={{display: 'flex', flexDirection: 'row'}}>
        {
          Object.keys(todos).sort((a,b) => sortingMap[todos[a].grade] - sortingMap[todos[b].grade]).map((title) => (
            <div style={{flex: 1}}>
              <h3 style={{textAlign: 'center', marginBottom: '4vh'}}>{title}</h3>
              <TodoList items={todos[title]} parent={title} markTodoDone={markTodoDone}/>
            </div>
          ))
        }
        </div>
      </div>
  );
}

export default App;