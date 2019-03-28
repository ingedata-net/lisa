SRC_DIR=./src
PROTO_SRC_DIR=./proto
PROTO_DST_DIR=$(SRC_DIR)/proto

proto: input.proto output.proto

input.proto:
	protoc -I=$(PROTO_SRC_DIR) --python_out=$(PROTO_DST_DIR) $(PROTO_SRC_DIR)/input.proto

output.proto:
	protoc -I=$(PROTO_SRC_DIR) --python_out=$(PROTO_DST_DIR) $(PROTO_SRC_DIR)/output.proto
