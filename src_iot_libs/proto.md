```
python -m grpc_tools.protoc -I. --python_out=. --pyi_out=. --grpc_python_out=. hub.proto
```

# References
[gRPC Examples](https://github.com/grpc/grpc/tree/master/examples/python)
[gRPC Concepts](https://github.com/grpc/grpc/blob/master/CONCEPTS.md)
[gRPC Protocol](https://github.com/grpc/grpc/blob/master/doc/PROTOCOL-HTTP2.md)