gen: 
	java -jar processing-py.jar sketch.py

bundle:
	pyinstaller main.py --onefile

clean:
	trash build; trash dist

# move executable to bin for testing.
shuffle:
	@echo "Removing old executable, copying over new..."; trash /usr/local/bin/QH; cp dist/main /usr/local/bin/QH;

dist: clean bundle shuffle