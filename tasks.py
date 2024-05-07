import os

from invoke.tasks import task

module_path = os.path.dirname(os.path.realpath(__file__))
path_to_format = module_path

dag_nao_req_in_file_path = os.path.join(module_path, "requirements.in")
dev_req_in_file_path = os.path.join(module_path, "requirements-dev.in")

dag_nao_req_txt_file_path = os.path.join(module_path, "requirements.txt")
dev_req_txt_file_path = os.path.join(module_path, "requirements-dev.txt")

tests_setup_module_path = os.path.join(module_path, "tests", "setup")


"""
UL TASKS
"""


@task
def install(c):
    c.run(f"pip install --no-cache-dir -e {module_path}/.[ci]")


"""
DEV TASKS
"""


@task
def format(c):
    c.run(f"isort --profile black {path_to_format}")
    c.run(f"black {path_to_format}")


@task
def formatcheck(c):
    c.run(f"isort --profile black {path_to_format} -c")
    c.run(f"black --check {path_to_format}")


@task
def pip_compile(c):
    c.run(
        f"""
          rm -r {dag_nao_req_txt_file_path}

          pip-compile \
            --rebuild \
            --no-emit-index-url \
            --no-header \
            --resolver=backtracking \
            -o {dag_nao_req_txt_file_path} \
            {dag_nao_req_in_file_path}

            rm -r {dev_req_txt_file_path}

            pip-compile \
            --rebuild \
            --no-emit-index-url \
            --no-header \
            --resolver=backtracking \
            -o {dev_req_txt_file_path}  \
            {dev_req_in_file_path}
          """,
        pty=True,
    )
    c.run(f"invoke install")
