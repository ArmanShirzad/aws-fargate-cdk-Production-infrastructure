.PHONY: bootstrap synth diff deploy destroy

bootstrap:
	cd deploy/cdk && cdk bootstrap

synth:
	cd deploy/cdk && cdk synth

diff:
	cd deploy/cdk && cdk diff

deploy:
	pip install -r deploy/cdk/requirements.txt
	cd deploy/cdk && cdk bootstrap && cdk deploy --require-approval never

destroy:
	cd deploy/cdk && cdk destroy

