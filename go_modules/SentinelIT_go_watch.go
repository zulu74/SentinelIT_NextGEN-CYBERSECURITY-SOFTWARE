package main

import (
	"fmt"
	"io/ioutil"
	"log"
	"os"
	"os/exec"
	"path/filepath"
	"time"
)

const (
	watchDir  = "./sandbox"
	logFile   = "sandboxwatch.log"
	interval  = 10 * time.Second
)

func main() {
	log.Println("Sandbox Watcher Started.")
	ensureDir(watchDir)
	for {
		files, err := ioutil.ReadDir(watchDir)
		if err != nil {
			log.Printf("Error reading directory: %v\n", err)
			continue
		}

		for _, file := range files {
			if filepath.Ext(file.Name()) == ".exe" {
				fullPath := filepath.Join(watchDir, file.Name())
				logAction(fmt.Sprintf("Executing: %s", fullPath))
				runAndLog(fullPath)
				err := os.Remove(fullPath)
				if err != nil {
					logAction(fmt.Sprintf("Error deleting: %s – %v", fullPath, err))
				} else {
					logAction(fmt.Sprintf("Deleted: %s", fullPath))
				}
			}
		}
		time.Sleep(interval)
	}
}

func runAndLog(path string) {
	cmd := exec.Command(path)
	output, err := cmd.CombinedOutput()
	logEntry := fmt.Sprintf("Output from %s:\n%s", path, string(output))
	logAction(logEntry)
	if err != nil {
		logAction(fmt.Sprintf("Execution error: %v", err))
	}
}

func logAction(entry string) {
	f, err := os.OpenFile(logFile, os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0644)
	if err != nil {
		log.Printf("Log error: %v\n", err)
		return
	}
	defer f.Close()
	logger := log.New(f, "", log.LstdFlags)
	logger.Println(entry)
}

func ensureDir(dir string) {
	if _, err := os.Stat(dir); os.IsNotExist(err) {
		err = os.Mkdir(dir, 0755)
		if err != nil {
			log.Fatalf("Failed to create directory: %v", err)
		}
	}
}
