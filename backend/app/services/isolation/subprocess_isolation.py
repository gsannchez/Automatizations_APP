import multiprocessing
import logging

logger = logging.getLogger(__name__)

class SubprocessIsolation:
    """
    Runs heavy GPU tasks in a completely separate process.
    When the process terminates, the OS forcefully reclaims all VRAM.
    """
    @staticmethod
    def _run_in_isolation(func, args, kwargs, return_dict):
        """Wrapper to execute function and store result in shared dict."""
        try:
            result = func(*args, **kwargs)
            return_dict['result'] = result
            return_dict['status'] = 'success'
        except Exception as e:
            logger.error(f"Isolated process crashed: {e}")
            return_dict['error'] = str(e)
            return_dict['status'] = 'error'

    @staticmethod
    def execute(func, *args, **kwargs):
        """
        Spawns a new process, runs the function, and returns the result.
        Blocks until the subprocess finishes.
        """
        manager = multiprocessing.Manager()
        return_dict = manager.dict()
        
        p = multiprocessing.Process(target=SubprocessIsolation._run_in_isolation, args=(func, args, kwargs, return_dict))
        p.start()
        p.join() # Wait for it to finish
        
        if return_dict.get('status') == 'error':
            raise RuntimeError(f"Isolated task failed: {return_dict.get('error')}")
            
        return return_dict.get('result')
