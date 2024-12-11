all: reset

clear-errs:
	@echo "Removing logs"
	-@rm ./*errors.log
	-@rm ./logs/*errors.log
	-@rm ./src/logs/*errors.log

clear-chats:
	@echo "Removing chat logs and checkpoints"
	-@rm ./*chats.log
	-@rm ./logs/*chats.log
	-@rm ./src/logs/*chats.log
	-@rm ./*chats.ckpt
	-@rm ./logs/*chats.ckpt
	-@rm ./src/logs/*chats.ckpt

kill:
	-pgrep -u jdolak python3
	-pkill -u jdolak python3

zip:
	tar -czf ./src.tar ./src/

tmp:
	-mkdir /tmp/jdolak

copy:
	cp ./condor.submit /tmp/jdolak 
	cp ./submit.sh /tmp/jdolak 
	cp ./src.tar /tmp/jdolak 

reset: kill clear-errs clear-chats