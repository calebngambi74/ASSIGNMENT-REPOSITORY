# Data Structure 1: Linked List Node
class Node:
    def __init__(self, student_id, name, program, year):
        self.student_id = student_id
        self.name = name
        self.program = program
        self.year = year
        self.next = None

# Data Structure 2: Stack for Undo Operations
class Stack:
    def __init__(self):
        self.items = []
    
    def push(self, item):
        self.items.append(item)
    
    def pop(self):
        if not self.is_empty():
            return self.items.pop()
        return None
    
    def is_empty(self):
        return len(self.items) == 0

# Data Structure 3: Queue for Registration Processing
class Queue:
    def __init__(self):
        self.items = []
    
    def enqueue(self, item):
        self.items.append(item)
    
    def dequeue(self):
        if not self.is_empty():
            return self.items.pop(0)
        return None
    
    def is_empty(self):
        return len(self.items) == 0
    
    def get_all(self):
        return self.items.copy()

# Main Student Manager using Hash Table and Linked List
class StudentManager:
    def __init__(self):
        # Hash Table: For O(1) search by student ID
        self.hash_table = {}
        
        # Linked List: For sequential storage
        self.head = None
        
        # Stack: For undo delete operations
        self.undo_stack = Stack()
        
        # Queue: For registration processing
        self.registration_queue = Queue()
    
    def add_student(self, student_id, name, program, year):
        # Check if student already exists in hash table
        if student_id in self.hash_table:
            return False
        
        # Create new node
        new_node = Node(student_id, name, program, year)
        
        # Add to hash table
        self.hash_table[student_id] = new_node
        
        # Add to linked list
        if self.head is None:
            self.head = new_node
        else:
            current = self.head
            while current.next:
                current = current.next
            current.next = new_node
        
        return True
    
    def search_student(self, student_id):
        # Hash table provides O(1) search
        node = self.hash_table.get(student_id)
        if node:
            return {
                'student_id': node.student_id,
                'name': node.name,
                'program': node.program,
                'year': node.year
            }
        return None
    
    def update_student(self, student_id, name, program, year):
        node = self.hash_table.get(student_id)
        if node:
            node.name = name
            node.program = program
            node.year = year
            return True
        return False
    
    def delete_student(self, student_id):
        if student_id not in self.hash_table:
            return False
        
        # Save to undo stack
        node = self.hash_table[student_id]
        self.undo_stack.push({
            'student_id': node.student_id,
            'name': node.name,
            'program': node.program,
            'year': node.year
        })
        
        # Remove from hash table
        del self.hash_table[student_id]
        
        # Remove from linked list
        if self.head and self.head.student_id == student_id:
            self.head = self.head.next
        else:
            current = self.head
            while current and current.next:
                if current.next.student_id == student_id:
                    current.next = current.next.next
                    break
                current = current.next
        
        return True
    
    def undo_delete(self):
        student_data = self.undo_stack.pop()
        if student_data:
            self.add_student(
                student_data['student_id'],
                student_data['name'],
                student_data['program'],
                student_data['year']
            )
            return True
        return False
    
    def get_all_students(self):
        students = []
        current = self.head
        while current:
            students.append({
                'student_id': current.student_id,
                'name': current.name,
                'program': current.program,
                'year': current.year
            })
            current = current.next
        return students
    
    def add_to_registration_queue(self, student_id):
        self.registration_queue.enqueue(student_id)
    
    def process_registration_queue(self):
        return self.registration_queue.dequeue()
    
    def get_registration_queue(self):
        return self.registration_queue.get_all()
