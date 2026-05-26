# Huffman Encoding Web Application

This project is a simple web application that demonstrates the **Huffman Encoding algorithm** using:

- **Frontend:** HTML, CSS, JavaScript
- **Backend:** Python Flask
- **Algorithm:** C Language

---

# Requirements

Before running the project, make sure the following are installed on your PC:

## 1. Python
Download and install Python:

https://www.python.org/downloads/

Verify installation:

```bash
python --version
```

---

## 2. Flask

Install Flask using pip:

```bash
pip install flask
```

---

## 3. GCC Compiler (Optional)

If `huffman.exe` is missing or you want to recompile the C program:

### Windows
Install MinGW:

https://www.mingw-w64.org/downloads/

##Check if MinGW is Already Installed

Open Command Prompt and run:


```bash
gcc --version
```

If installed correctly, you will see output similar to:

```bash
gcc (MinGW-W64) x.x.x
```

---

# Project Setup

## Step 1: Download the Project

Extract the project folder:

```text
huffman-main/
```

---

## Step 2: Open Terminal in Project Folder

Navigate to the project directory:

```bash
cd huffman-main
```

---

# Compile the C Program (Optional)

If `huffman.exe` already exists, you can skip this step.

## Windows

```bash
gcc huffman.c -o huffman.exe
```

## Linux/macOS

```bash
gcc huffman.c -o huffman
```

---

# Run the Flask Application

Start the Flask server:

```bash
python app.py
```

If successful, you will see output similar to:

```bash
* Running on http://127.0.0.1:5000/
```

---

# Open in Browser

Open your browser and visit:

```text
http://127.0.0.1:5000/
```

You can now use the Huffman Encoding web application.

---

# Project Structure

```text
huffman-main/
├── app.py
├── huffman.c
├── huffman.exe
├── static/
│   ├── script.js
│   └── style.css
└── templates/
    └── index.html
```

---

# Stop the Server

Press:

```bash
CTRL + C
```

in the terminal to stop the Flask server.
