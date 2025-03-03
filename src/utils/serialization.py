import pickle
from basic_multi_processor import worker_init, LogSystem

def main():
    log_system = LogSystem()
    try:
        pickle.dumps(worker_init(log_system.log_queue))
        assert True
    except Exception:
        assert False, "序列化失败"
    finally:
        log_system.shutdown()

if __name__ == "__main__":
    main()