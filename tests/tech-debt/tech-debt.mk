.PHONY: \
		install-ack \
		review-tech-debt \
		count-tech-debt

ACK_BIN := $(shell which ack)
ACK := ack -ri --ignore-dir=.git --ignore-dir=tests/tech-debt

install-ack:
ifeq ('$(ACK_BIN)','')
	sudo apt-get install -y ack-grep
endif

review-tech-debt: install-ack
	@$(ACK) -A 5 '# YELLOW[\W]' . || true
	@$(ACK) -A 5 '# ORANGE[\W]' . || true
	@$(ACK) -A 5 '# RED'[\W] . || true

test-tech-debt: review-tech-debt install-ack
	@$(info Tech debt totals:)
	@$(info Yellow: $(shell $(ACK) '# YELLOW[\W]' . | wc -l))
	@$(info Orange: $(shell $(ACK) '# ORANGE[\W]' . | wc -l))
	@$(info Red: $(shell $(ACK) '# RED[\W]' . | wc -l))
	@if $(ACK) '# RED[\W]' . ; then \
	  	echo "You have RED tech debt! Please don't merge this!"; \
		exit 2; \
	fi
